#======================================
#--- Views de Gestão de Produtos ---
#======================================
# estoque/views.py

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import Q, Sum, F, Value, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from PIL import Image, UnidentifiedImageError
from usuarios.decorators import admin_requerido, estoquista_ou_admin
from suplastock.utils.export import PDFExporter, ExcelExporter
from vendas.models import Venda
from .models import Produto, Categoria, Fornecedor, AlertaEstoque, MovimentacaoEstoque
import logging

logger = logging.getLogger(__name__)

ALLOWED_IMAGE_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
ALLOWED_IMAGE_FORMATS = {'JPEG', 'PNG', 'WEBP'}


def _parse_bool(raw_value):
    return str(raw_value or '').strip().lower() in {'1', 'true', 'on', 'yes', 'sim'}


def _apply_status_filter(produtos, status_estoque):
    status = (status_estoque or '').strip().lower()
    if not status:
        return produtos

    if status == 'esgotado':
        return produtos.filter(estoque_atual=0)
    if status == 'critico':
        return produtos.filter(estoque_atual__gt=0, estoque_atual__lte=F('estoque_minimo'))
    if status == 'baixo':
        return produtos.filter(
            estoque_atual__gt=F('estoque_minimo'),
            estoque_atual__lte=F('estoque_minimo') + Value(3),
        )
    if status == 'normal':
        return produtos.filter(estoque_atual__gt=F('estoque_minimo') + Value(3))

    return produtos


def _apply_price_filter(produtos, faixa_preco):
    faixa = (faixa_preco or '').strip().lower()
    if not faixa:
        return produtos

    if faixa == 'ate_100':
        return produtos.filter(preco_venda_sugerido__lte=Decimal('100'))
    if faixa == '100_300':
        return produtos.filter(preco_venda_sugerido__gt=Decimal('100'), preco_venda_sugerido__lte=Decimal('300'))
    if faixa == '300_600':
        return produtos.filter(preco_venda_sugerido__gt=Decimal('300'), preco_venda_sugerido__lte=Decimal('600'))
    if faixa == 'acima_600':
        return produtos.filter(preco_venda_sugerido__gt=Decimal('600'))

    return produtos


def _build_produtos_queryset(
    *,
    search='',
    categoria_id='',
    fornecedor='',
    status_estoque='',
    faixa_preco='',
    apenas_esgotados=False,
):
    produtos = Produto.objects.select_related('categoria', 'fornecedor').all()

    if search:
        produtos = produtos.filter(
            Q(nome__icontains=search)
            | Q(sku__icontains=search)
            | Q(fornecedor__nome__icontains=search)
            | Q(fornecedor_nome_legado__icontains=search)
        )

    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)

    if fornecedor:
        produtos = produtos.filter(
            Q(fornecedor__nome__icontains=fornecedor)
            | Q(fornecedor_nome_legado__icontains=fornecedor)
        )

    produtos = _apply_status_filter(produtos, status_estoque)
    produtos = _apply_price_filter(produtos, faixa_preco)

    if apenas_esgotados:
        produtos = produtos.filter(estoque_atual=0)

    return produtos


def _parse_positive_int(raw_value, field_name, allow_zero=False):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} inválido.')
    if allow_zero:
        if value < 0:
            raise ValueError(f'{field_name} não pode ser negativo.')
    elif value <= 0:
        raise ValueError(f'{field_name} deve ser maior que zero.')
    return value


def _parse_decimal(raw_value, field_name, allow_zero=False):
    raw_text = str(raw_value if raw_value is not None else '').strip()
    if not raw_text:
        raise ValueError(f'{field_name} inválido.')

    # Normaliza formatos monetários comuns: "R$ 1.234,56" / "1234,56" / "1234.56"
    normalized = raw_text.replace('R$', '').replace(' ', '')
    if ',' in normalized and '.' in normalized:
        normalized = normalized.replace('.', '').replace(',', '.')
    elif ',' in normalized:
        normalized = normalized.replace(',', '.')

    try:
        value = Decimal(normalized)
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{field_name} inválido.')

    if not value.is_finite():
        raise ValueError(f'{field_name} inválido.')

    # Limite alinhado aos DecimalField(max_digits=10, decimal_places=2).
    max_decimal_field_value = Decimal('99999999.99')
    if value.copy_abs() > max_decimal_field_value:
        raise ValueError(
            f'{field_name} excede o limite permitido ({str(max_decimal_field_value).replace(".", ",")}).'
        )

    # Uniformiza escala para evitar falhas de conversão no backend do banco.
    try:
        value = value.quantize(Decimal('0.01'))
    except InvalidOperation:
        raise ValueError(f'{field_name} inválido.')

    if allow_zero:
        if value < 0:
            raise ValueError(f'{field_name} não pode ser negativo.')
    elif value <= 0:
        raise ValueError(f'{field_name} deve ser maior que zero.')
    return value


def _gerar_sku_unico_por_nome(nome, produto_id=None):
    nome_normalizado = (nome or '').strip()
    instancia = Produto(nome=nome_normalizado)
    if produto_id:
        instancia.pk = produto_id
    return instancia._gerar_sku_unico()


def _validate_uploaded_image(image_file):
    """Valida tipo, tamanho e dimensões da imagem enviada."""
    if not image_file:
        return

    content_type = (getattr(image_file, 'content_type', '') or '').lower()
    if content_type and content_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ValueError('Formato de imagem não permitido. Use JPG, PNG ou WEBP.')

    max_bytes = int(getattr(settings, 'PRODUTO_IMAGE_MAX_BYTES', 5 * 1024 * 1024))
    if image_file.size > max_bytes:
        max_mb = max_bytes / (1024 * 1024)
        raise ValueError(f'Imagem excede o tamanho máximo permitido ({max_mb:.0f} MB).')

    try:
        image_file.seek(0)
        with Image.open(image_file) as image:
            image.verify()

        image_file.seek(0)
        with Image.open(image_file) as image:
            image_format = (image.format or '').upper()
            width, height = image.size
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValueError('Arquivo de imagem inválido ou corrompido.')
    finally:
        image_file.seek(0)

    if image_format not in ALLOWED_IMAGE_FORMATS:
        raise ValueError('Formato de imagem não permitido. Use JPG, PNG ou WEBP.')

    max_width = int(getattr(settings, 'PRODUTO_IMAGE_MAX_WIDTH', 4096))
    max_height = int(getattr(settings, 'PRODUTO_IMAGE_MAX_HEIGHT', 4096))
    if width > max_width or height > max_height:
        raise ValueError(
            f'Dimensões da imagem excedem o limite permitido ({max_width}x{max_height}px).'
        )


def _registrar_movimentacao(produto, tipo, quantidade, usuario=None, observacao=''):
    quantidade_int = int(quantidade or 0)
    if quantidade_int <= 0:
        return

    MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo_movimentacao=tipo,
        quantidade=quantidade_int,
        usuario_responsavel=usuario if getattr(usuario, 'is_authenticated', False) else None,
        observacao=(observacao or '').strip() or None,
    )


def _filtros_request(request):
    return {
        'search': (request.GET.get('search') or '').strip(),
        'categoria_id': (request.GET.get('categoria') or '').strip(),
        'fornecedor': (request.GET.get('fornecedor') or '').strip(),
        'status_estoque': (request.GET.get('status_estoque') or '').strip(),
        'faixa_preco': (request.GET.get('faixa_preco') or '').strip(),
        'apenas_esgotados': _parse_bool(request.GET.get('apenas_esgotados')),
        'ordenar': (request.GET.get('ordenar') or 'recentes').strip(),
    }


def _aplicar_tipo_exportacao(produtos, tipo_exportacao):
    tipo = (tipo_exportacao or 'completo').strip().lower()

    if tipo == 'esgotados':
        return produtos.filter(estoque_atual=0)
    if tipo == 'baixo_estoque':
        return produtos.filter(estoque_atual__gt=0, estoque_atual__lte=F('estoque_minimo') + Value(3))
    if tipo == 'financeiro':
        return produtos
    return produtos


# Views para gestão de produtos, categorias e fornecedores
@login_required
def gestao_produtos(request):
    """View para listagem de produtos"""
    categorias = Categoria.objects.all().order_by('nome')

    filtros = _filtros_request(request)

    lucro_expr = ExpressionWrapper(
        F('preco_venda_sugerido') - F('preco_custo_unitario'),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    produtos = (
        _build_produtos_queryset(
            search=filtros['search'],
            categoria_id=filtros['categoria_id'],
            fornecedor=filtros['fornecedor'],
            status_estoque=filtros['status_estoque'],
            faixa_preco=filtros['faixa_preco'],
            apenas_esgotados=filtros['apenas_esgotados'],
        )
        .annotate(
            total_vendido=Coalesce(Sum('venda__quantidade_vendida'), Value(0)),
            lucro_unitario_calc=lucro_expr,
        )
    )

    ordenacao = filtros['ordenar']
    if ordenacao == 'lucro_desc':
        produtos = produtos.order_by('-lucro_unitario_calc', 'nome')
    elif ordenacao == 'lucro_asc':
        produtos = produtos.order_by('lucro_unitario_calc', 'nome')
    elif ordenacao == 'preco_desc':
        produtos = produtos.order_by('-preco_venda_sugerido', 'nome')
    elif ordenacao == 'preco_asc':
        produtos = produtos.order_by('preco_venda_sugerido', 'nome')
    elif ordenacao == 'mais_vendidos':
        produtos = produtos.order_by('-total_vendido', 'nome')
    else:
        produtos = produtos.order_by('-data_compra', '-id')

    valor_estoque_expr = ExpressionWrapper(
        F('preco_custo_unitario') * F('estoque_atual'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    total_produtos = produtos.count()
    valor_estoque = produtos.aggregate(total=Coalesce(Sum(valor_estoque_expr), Value(Decimal('0.00'))))['total']
    produtos_estoque_baixo = produtos.filter(estoque_atual__gt=F('estoque_minimo'), estoque_atual__lte=F('estoque_minimo') + Value(3)).count()
    produtos_estoque_critico = produtos.filter(estoque_atual__gt=0, estoque_atual__lte=F('estoque_minimo')).count()
    produtos_esgotados = produtos.filter(estoque_atual=0).count()

    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)

    lucro_total_expr = ExpressionWrapper(
        (F('preco_venda_unitario') - F('produto__preco_custo_unitario')) * F('quantidade_vendida'),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )

    vendas_mes = (
        Venda.objects
        .filter(data_venda__gte=inicio_mes, data_venda__lte=hoje)
        .values('produto_id', 'produto__nome', 'produto__sku')
        .annotate(
            total_quantidade=Coalesce(Sum('quantidade_vendida'), Value(0)),
            lucro_total=Coalesce(Sum(lucro_total_expr), Value(Decimal('0.00'))),
        )
    )

    produto_mais_vendido = vendas_mes.order_by('-total_quantidade', 'produto__nome').first()
    produto_mais_lucrativo = vendas_mes.order_by('-lucro_total', 'produto__nome').first()

    paginator = Paginator(produtos, 10)
    page_number = request.GET.get('page')
    produtos_paginados = paginator.get_page(page_number)

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()

    fornecedores_disponiveis = sorted({
        nome.strip()
        for nome in (
            list(Fornecedor.objects.filter(ativo=True).values_list('nome', flat=True))
            + list(
                Produto.objects
                .exclude(fornecedor_nome_legado__isnull=True)
                .exclude(fornecedor_nome_legado='')
                .values_list('fornecedor_nome_legado', flat=True)
            )
        )
        if nome and nome.strip()
    })

    context = {
        'produtos': produtos_paginados,
        'categorias': categorias,
        'fornecedores_disponiveis': fornecedores_disponiveis,
        'search': filtros['search'],
        'categoria_selecionada': filtros['categoria_id'],
        'fornecedor_selecionado': filtros['fornecedor'],
        'status_estoque_selecionado': filtros['status_estoque'],
        'faixa_preco_selecionada': filtros['faixa_preco'],
        'apenas_esgotados': filtros['apenas_esgotados'],
        'ordenacao_selecionada': ordenacao,
        'total_produtos': total_produtos,
        'valor_estoque': valor_estoque,
        'produtos_estoque_baixo': produtos_estoque_baixo,
        'produtos_estoque_critico': produtos_estoque_critico,
        'produtos_esgotados': produtos_esgotados,
        'produto_mais_vendido': produto_mais_vendido,
        'produto_mais_lucrativo': produto_mais_lucrativo,
        'filtros_ativos': bool(
            filtros['search']
            or filtros['categoria_id']
            or filtros['fornecedor']
            or filtros['status_estoque']
            or filtros['faixa_preco']
            or filtros['apenas_esgotados']
            or ordenacao != 'recentes'
        ),
        'query_string': query_string,
        'ultima_atualizacao': timezone.localtime(timezone.now()),
    }
    return render(request, 'estoque/gestao_de_produtos.html', context)


@login_required
def api_produtos_todos(request):
    """API para retornar todos os produtos em JSON para o modal."""
    produtos = Produto.objects.select_related('categoria').all().order_by('nome')

    produtos_data = []
    for p in produtos:
        produtos_data.append({
            'id': p.id,
            'sku': p.sku or '',
            'nome': p.nome,
            'categoria_id': p.categoria_id,
            'categoria_nome': p.categoria.nome if p.categoria else 'Sem categoria',
            'estoque_atual': p.estoque_atual,
            'estoque_minimo': p.estoque_minimo,
            'preco_custo_unitario': str(p.preco_custo_unitario),
            'preco_venda_sugerido': str(p.preco_venda_sugerido),
            'lucro_unitario': str(p.lucro_unitario),
            'status_estoque': p.status_estoque,
        })

    return JsonResponse({'produtos': produtos_data}, safe=False)


@login_required
def api_produto_detalhes(request, produto_id):
    """API de detalhes completos de um produto para modal de visualização."""
    produto = get_object_or_404(
        Produto.objects.select_related('categoria', 'fornecedor'),
        id=produto_id,
    )

    total_vendido = (
        Venda.objects
        .filter(produto_id=produto.id)
        .aggregate(total=Coalesce(Sum('quantidade_vendida'), Value(0)))['total']
    )

    movimentacoes = (
        MovimentacaoEstoque.objects
        .filter(produto_id=produto.id)
        .select_related('usuario_responsavel')
        .order_by('-data_movimentacao')[:50]
    )

    historico = []
    for mov in movimentacoes:
        responsavel = 'Sistema'
        if mov.usuario_responsavel:
            responsavel = (
                mov.usuario_responsavel.get_full_name().strip()
                or mov.usuario_responsavel.username
            )

        historico.append({
            'data': timezone.localtime(mov.data_movimentacao).strftime('%d/%m/%Y %H:%M'),
            'tipo': mov.get_tipo_movimentacao_display(),
            'quantidade': mov.quantidade_com_sinal,
            'responsavel': responsavel,
            'observacao': mov.observacao or '-',
        })

    fornecedor_nome = (
        produto.fornecedor.nome
        if produto.fornecedor_id
        else (produto.fornecedor_nome_legado or '-')
    )

    payload = {
        'id': produto.id,
        'nome': produto.nome,
        'sku': produto.sku or '-',
        'categoria': produto.categoria.nome if produto.categoria else 'Sem categoria',
        'fornecedor': fornecedor_nome,
        'data_cadastro': timezone.localtime(produto.criado_em).strftime('%d/%m/%Y %H:%M'),
        'ultima_atualizacao': timezone.localtime(produto.atualizado_em).strftime('%d/%m/%Y %H:%M'),
        'quantidade_comprada': int(produto.quantidade_comprada or 0),
        'quantidade_vendida': int(total_vendido or 0),
        'estoque_atual': int(produto.estoque_atual or 0),
        'estoque_minimo': int(produto.estoque_minimo or 0),
        'status_estoque': produto.status_estoque,
        'preco_custo': float(produto.preco_custo_unitario or 0),
        'preco_venda': float(produto.preco_venda_sugerido or 0),
        'lucro_unitario': float(produto.lucro_unitario or 0),
        'margem_lucro': float(produto.margem_lucro_percentual or 0),
        'historico': historico,
    }
    return JsonResponse(payload)


@login_required
@estoquista_ou_admin
def api_sku_preview(request):
    nome = (request.GET.get('nome') or '').strip()
    if not nome:
        return JsonResponse({'sku': ''})

    sku = _gerar_sku_unico_por_nome(nome)
    return JsonResponse({'sku': sku})


# Views para cadastro, edição e exclusão de produtos
@login_required
@estoquista_ou_admin
def cadastrar_produto(request):
    """View para cadastrar produto"""
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        nome = (request.POST.get('nome') or '').strip()
        categoria_id = request.POST.get('categoria')
        fornecedor_nome = request.POST.get('fornecedor')
        quantidade_comprada = request.POST.get('quantidade_comprada')
        preco_custo_unitario = request.POST.get('preco_custo_unitario')
        preco_venda_sugerido = request.POST.get('preco_venda_sugerido')
        data_compra = request.POST.get('data_compra')
        imagem = request.FILES.get('imagem')

        if not all([nome, quantidade_comprada, preco_custo_unitario, data_compra]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return HttpResponseRedirect(reverse('estoque:cadastrar_produto'))

        try:
            quantidade_comprada_int = _parse_positive_int(quantidade_comprada, 'Quantidade')
            preco_custo_decimal = _parse_decimal(preco_custo_unitario, 'Preço de custo')
            preco_venda_decimal = _parse_decimal(
                preco_venda_sugerido or 0,
                'Preço de venda',
                allow_zero=True,
            )
            _validate_uploaded_image(imagem)
        except ValueError as exc:
            messages.error(request, str(exc))
            return HttpResponseRedirect(reverse('estoque:cadastrar_produto'))

        try:
            with transaction.atomic():
                sku_gerado = _gerar_sku_unico_por_nome(nome)
                produto = Produto.objects.create(
                    nome=nome,
                    sku=sku_gerado,
                    categoria_id=categoria_id if categoria_id else None,
                    fornecedor_nome_legado=(fornecedor_nome or '').strip() or None,
                    quantidade_comprada=quantidade_comprada_int,
                    preco_custo_unitario=preco_custo_decimal,
                    preco_venda_sugerido=preco_venda_decimal,
                    estoque_atual=quantidade_comprada_int,
                    data_compra=data_compra,
                    imagem=imagem,
                )
                _registrar_movimentacao(
                    produto,
                    'entrada',
                    quantidade_comprada_int,
                    usuario=request.user,
                    observacao='Cadastro inicial do produto',
                )
        except IntegrityError:
            messages.error(request, 'Não foi possível gerar um SKU único agora. Tente novamente.')
            return HttpResponseRedirect(reverse('estoque:cadastrar_produto'))
        except (InvalidOperation, ValueError, OverflowError):
            messages.error(
                request,
                'Valores monetários inválidos. Verifique preço de custo e preço de venda.',
            )
            return HttpResponseRedirect(reverse('estoque:cadastrar_produto'))
        except DatabaseError as exc:
            logger.exception('Erro de banco ao cadastrar produto: %s', exc)
            messages.error(request, 'Erro ao cadastrar produto. Tente novamente.')
            return HttpResponseRedirect(reverse('estoque:cadastrar_produto'))

        messages.success(request, f'Produto "{nome}" cadastrado com sucesso!')
        return HttpResponseRedirect(reverse('estoque:gestao_produtos'))

    context = {'categorias': categorias}
    return render(request, 'estoque/cadastrar_produto.html', context)


# Views para edição e exclusão de produtos
@login_required
@estoquista_ou_admin
def editar_produto(request, produto_id):
    """View para editar produto"""
    produto = get_object_or_404(Produto, id=produto_id)
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        categoria_id = request.POST.get('categoria')
        preco_venda_sugerido = request.POST.get('preco_venda_sugerido')
        nova_imagem = request.FILES.get('imagem')
        sku = (request.POST.get('sku') or '').strip().upper()
        nome = (request.POST.get('nome') or '').strip()

        if not nome:
            messages.error(request, 'Nome do produto é obrigatório.')
            return HttpResponseRedirect(reverse('estoque:gestao_produtos'))

        try:
            quantidade_adicionada = _parse_positive_int(
                request.POST.get('quantidade_adicionada') or 0,
                'Quantidade a adicionar',
                allow_zero=True,
            )
            novo_preco_custo = _parse_decimal(
                request.POST.get('preco_custo_unitario'),
                'Preço de custo',
            )
            novo_preco_venda = _parse_decimal(
                preco_venda_sugerido or produto.preco_venda_sugerido,
                'Preço de venda',
                allow_zero=True,
            )
            _validate_uploaded_image(nova_imagem)
        except ValueError as exc:
            messages.error(request, str(exc))
            return HttpResponseRedirect(reverse('estoque:gestao_produtos'))

        produto.nome = nome
        produto.sku = sku or None
        produto.categoria_id = categoria_id if categoria_id else None
        produto.fornecedor_nome_legado = (request.POST.get('fornecedor') or '').strip() or None
        produto.quantidade_comprada = int(produto.quantidade_comprada or 0) + quantidade_adicionada
        produto.estoque_atual = int(produto.estoque_atual or 0) + quantidade_adicionada
        produto.preco_custo_unitario = novo_preco_custo
        produto.preco_venda_sugerido = novo_preco_venda
        produto.data_compra = request.POST.get('data_compra')

        if nova_imagem:
            produto.imagem = nova_imagem

        try:
            with transaction.atomic():
                produto.save()

                if quantidade_adicionada > 0:
                    _registrar_movimentacao(
                        produto,
                        'entrada',
                        quantidade_adicionada,
                        usuario=request.user,
                        observacao='Entrada por reposição manual de estoque',
                    )
        except IntegrityError:
            messages.error(request, 'SKU já está em uso. Informe outro código.')
            return HttpResponseRedirect(reverse('estoque:gestao_produtos'))
        except (InvalidOperation, ValueError, OverflowError):
            messages.error(
                request,
                'Valores monetários inválidos. Verifique preço de custo e preço de venda.',
            )
            return HttpResponseRedirect(reverse('estoque:gestao_produtos'))
        except DatabaseError as exc:
            logger.exception('Erro de banco ao editar produto id=%s: %s', produto_id, exc)
            messages.error(request, 'Erro ao atualizar produto. Tente novamente.')
            return HttpResponseRedirect(reverse('estoque:gestao_produtos'))

        messages.success(request, f'Produto "{produto.nome}" atualizado com sucesso!')
        return HttpResponseRedirect(reverse('estoque:gestao_produtos'))

    context = {
        'produto': produto,
        'categorias': categorias,
    }
    return render(request, 'estoque/editar_produto.html', context)


# Views para exclusão de produtos
@login_required
@estoquista_ou_admin
@require_POST
def deletar_produto(request, produto_id):
    """View para deletar produto"""
    produto = get_object_or_404(Produto, id=produto_id)
    nome = produto.nome
    produto.delete()
    messages.success(request, f'Produto "{nome}" deletado com sucesso!')
    return HttpResponseRedirect(reverse('estoque:gestao_produtos'))


# Views para relatórios de estoque e alertas
@login_required
@admin_requerido
def relatorio_estoque(request):
    """Relatório de estoque com alertas"""
    estoque_baixo = Produto.objects.filter(
        estoque_atual__lte=F('estoque_minimo'),
        ativo=True,
    ).order_by('estoque_atual')
    data_limite = timezone.now().date() + timedelta(days=30)
    proximo_vencimento = Produto.objects.filter(
        data_validade__lte=data_limite,
        data_validade__gte=timezone.now().date(),
        ativo=True,
    ).order_by('data_validade')
    vencidos = Produto.objects.filter(
        data_validade__lt=timezone.now().date(),
        ativo=True,
    ).order_by('data_validade')
    zerados = Produto.objects.filter(
        estoque_atual=0,
        ativo=True,
    )
    context = {
        'estoque_baixo': estoque_baixo,
        'proximo_vencimento': proximo_vencimento,
        'vencidos': vencidos,
        'zerados': zerados,
    }
    return render(request, 'estoque/relatorios/estoque.html', context)


# Views para exportação de relatórios
@login_required
@admin_requerido
def exportar_estoque_pdf(request):
    """Exporta relatório de estoque em PDF"""
    filtros = _filtros_request(request)
    tipo_exportacao = (request.GET.get('tipo_exportacao') or 'completo').strip().lower()

    produtos = _build_produtos_queryset(
        search=filtros['search'],
        categoria_id=filtros['categoria_id'],
        fornecedor=filtros['fornecedor'],
        status_estoque=filtros['status_estoque'],
        faixa_preco=filtros['faixa_preco'],
        apenas_esgotados=filtros['apenas_esgotados'],
    ).order_by('nome')

    produtos = _aplicar_tipo_exportacao(produtos, tipo_exportacao)
    return PDFExporter.exportar_estoque(produtos, tipo_exportacao=tipo_exportacao)


@login_required
@admin_requerido
def exportar_estoque_excel(request):
    """Exporta relatório de estoque em Excel."""
    filtros = _filtros_request(request)
    tipo_exportacao = (request.GET.get('tipo_exportacao') or 'completo').strip().lower()

    produtos = _build_produtos_queryset(
        search=filtros['search'],
        categoria_id=filtros['categoria_id'],
        fornecedor=filtros['fornecedor'],
        status_estoque=filtros['status_estoque'],
        faixa_preco=filtros['faixa_preco'],
        apenas_esgotados=filtros['apenas_esgotados'],
    ).order_by('nome')

    produtos = _aplicar_tipo_exportacao(produtos, tipo_exportacao)
    return ExcelExporter.exportar_estoque(produtos, tipo_exportacao=tipo_exportacao)

