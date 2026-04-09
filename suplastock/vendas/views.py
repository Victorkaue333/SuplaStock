# vendas/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from usuarios.decorators import admin_requerido, vendedor_ou_admin
from suplastock.utils.export import PDFExporter, ExcelExporter
from estoque.models import Produto, MovimentacaoEstoque
from financeiro.models import ContaReceber
from .models import Cliente, Venda, Pagamento
import logging

logger = logging.getLogger(__name__)


def _log_operational_error(event, request, exc, **context):
    user_id = getattr(getattr(request, 'user', None), 'id', None)
    logger.exception(
        'event=%s module=vendas user_id=%s method=%s path=%s context=%s error=%s',
        event,
        user_id,
        request.method,
        request.path,
        context,
        exc.__class__.__name__,
    )


def _parse_positive_decimal(raw_value, field_name):
    try:
        value = Decimal(str(raw_value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f'{field_name} invÃ¡lido.')
    if value <= 0:
        raise ValueError(f'{field_name} deve ser maior que zero.')
    return value


def _parse_positive_int(raw_value, field_name):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(f'{field_name} invÃ¡lido.')
    if value <= 0:
        raise ValueError(f'{field_name} deve ser maior que zero.')
    return value


def _normalizar_forma_pagamento(raw_value):
    aliases = {
        'pix': 'Pix',
        'dinheiro': 'Dinheiro',
        'cartao de crÃ©dito': 'CartÃ£o de CrÃ©dito',
        'cartÃ£o de crÃ©dito': 'CartÃ£o de CrÃ©dito',
        'cartao_credito': 'CartÃ£o de CrÃ©dito',
        'cartÃ£o_credito': 'CartÃ£o de CrÃ©dito',
        'cartao de debito': 'CartÃ£o de DÃ©bito',
        'cartÃ£o de dÃ©bito': 'CartÃ£o de DÃ©bito',
        'cartao_debito': 'CartÃ£o de DÃ©bito',
        'cartÃ£o_debito': 'CartÃ£o de DÃ©bito',
        'transferencia': 'TransferÃªncia',
        'transferÃªncia': 'TransferÃªncia',
    }
    valor_normalizado = aliases.get((raw_value or '').strip().lower(), (raw_value or '').strip())
    if valor_normalizado not in dict(Pagamento.FORMAS_PAGAMENTO):
        raise ValueError('Forma de pagamento invÃ¡lida.')
    return valor_normalizado


def _format_currency_br(value):
    amount = Decimal(str(value or 0)).quantize(Decimal('0.01'))
    is_negative = amount < 0
    amount = abs(amount)
    integer_part, decimal_part = f'{amount:.2f}'.split('.')
    integer_part = f'{int(integer_part):,}'.replace(',', '.')
    signal = '-' if is_negative else ''
    return f'{signal}R$ {integer_part},{decimal_part}'


def _registrar_movimentacao_estoque(produto, tipo, quantidade, request, observacao=''):
    quantidade_int = int(quantidade or 0)
    if quantidade_int <= 0:
        return
    MovimentacaoEstoque.objects.create(
        produto=produto,
        tipo_movimentacao=tipo,
        quantidade=quantidade_int,
        usuario_responsavel=request.user if getattr(request.user, 'is_authenticated', False) else None,
        observacao=(observacao or '').strip() or None,
    )


def _consolidar_status_pagamento(statuses):
    status_set = {str(status or '').strip() for status in statuses if str(status or '').strip()}
    if not status_set:
        return 'Pago'
    if status_set == {'Pendente'}:
        return 'Fiado'
    if status_set == {'Pago'}:
        return 'Pago'
    if status_set == {'Parcial'}:
        return 'Parcial'
    return 'Parcial'


def _obter_ou_criar_cliente_por_nome(cliente_nome):
    cliente = (
        Cliente.objects
        .filter(nome__iexact=cliente_nome)
        .order_by('id')
        .first()
    )
    cliente_criado = False
    codigo_gerado = False

    if not cliente:
        cliente = Cliente.objects.create(nome=cliente_nome)
        cliente_criado = True
        codigo_gerado = bool(cliente.codigo)
    elif not (cliente.codigo or '').strip():
        cliente.save()
        codigo_gerado = bool(cliente.codigo)

    return cliente, cliente_criado, codigo_gerado


def _resolve_export_period(request):
    data_inicio_raw = (request.GET.get('data_inicio') or '').strip()
    data_fim_raw = (request.GET.get('data_fim') or '').strip()
    mes_raw = (request.GET.get('mes') or '').strip()
    hoje = timezone.localtime(timezone.now()).date()

    if data_inicio_raw and data_fim_raw:
        try:
            data_inicio = datetime.strptime(data_inicio_raw, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_raw, '%Y-%m-%d').date()
            if data_inicio > data_fim:
                data_inicio, data_fim = data_fim, data_inicio
            return data_inicio, data_fim
        except ValueError:
            pass

    if mes_raw:
        try:
            ano, mes = mes_raw.split('-')
            ano = int(ano)
            mes = int(mes)
            if 1 <= mes <= 12:
                data_inicio = date(ano, mes, 1)
                if mes == 12:
                    data_fim = date(ano + 1, 1, 1) - timedelta(days=1)
                else:
                    data_fim = date(ano, mes + 1, 1) - timedelta(days=1)
                return data_inicio, data_fim
        except (TypeError, ValueError):
            pass

    data_inicio = hoje.replace(day=1)
    data_fim = hoje
    return data_inicio, data_fim


def _build_vendas_export_queryset(request):
    data_inicio, data_fim = _resolve_export_period(request)
    vendas = Venda.objects.filter(data_venda__range=[data_inicio, data_fim])

    produto_raw = (request.GET.get('produto') or '').strip()
    if produto_raw:
        try:
            vendas = vendas.filter(produto_id=int(produto_raw))
        except (TypeError, ValueError):
            pass

    cliente_raw = (request.GET.get('cliente') or '').strip()
    if cliente_raw:
        vendas = vendas.filter(
            Q(cliente__nome__icontains=cliente_raw)
            | Q(cliente__codigo__icontains=cliente_raw)
            | Q(cliente_nome_legado__icontains=cliente_raw)
        )

    tipo_pagamento_raw = (request.GET.get('tipo_pagamento') or '').strip()
    if tipo_pagamento_raw:
        vendas = vendas.filter(forma_pagamento_legado__iexact=tipo_pagamento_raw)

    vendas = vendas.select_related('produto', 'cliente').order_by('-data_venda')
    return vendas, data_inicio, data_fim


# ========================= NOTA FISCAL =========================

@login_required
@vendedor_ou_admin
def emitir_nota_fiscal(request):
    """Tela de emissÃ£o de nota fiscal baseada nas vendas realizadas"""
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    if request.method == 'POST':
        transacao_id = request.POST.get('transacao_id')
        produto_id = request.POST.get('produto_id')
        cliente_id = request.POST.get('cliente_id')
        quantidade = request.POST.get('quantidade')
        valor_unitario = request.POST.get('valor_unitario')
        valor_total = request.POST.get('valor_total')
        try:
            cliente_nome = None
            produto_nome = None
            if cliente_id:
                cliente = Cliente.objects.filter(id=cliente_id).first()
                cliente_nome = cliente.nome if cliente else 'Cliente nÃ£o encontrado'
            if produto_id:
                produto = Produto.objects.filter(id=produto_id).first()
                produto_nome = produto.nome if produto else 'Produto nÃ£o encontrado'

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, y, "Nota Fiscal - SuplaStock")
            p.setFont("Helvetica", 12)
            y -= 40
            p.drawString(50, y, f"Cliente: {cliente_nome}")
            y -= 25
            p.drawString(50, y, f"Produto: {produto_nome}")
            y -= 25
            p.drawString(50, y, f"Quantidade: {quantidade}")
            y -= 25
            p.drawString(50, y, f"Valor UnitÃ¡rio: R$ {valor_unitario}")
            y -= 25
            p.drawString(50, y, f"Valor Total: R$ {valor_total}")
            y -= 25
            p.drawString(50, y, f"Data de EmissÃ£o: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            y -= 40
            p.setFont("Helvetica-Oblique", 10)
            p.drawString(50, y, "Documento gerado automaticamente pelo sistema.")
            p.showPage()
            p.save()
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="nota_fiscal_{cliente_nome}_{produto_nome}.pdf"'
            return response
        except (ValueError, TypeError, DatabaseError, OSError) as exc:
            _log_operational_error(
                'emitir_nota_fiscal_pdf',
                request,
                exc,
                transacao_id=transacao_id,
                cliente_id=cliente_id,
                produto_id=produto_id,
            )
            messages.error(request, 'Erro ao emitir nota fiscal.')

    cliente_nome = request.GET.get('cliente', '').strip()
    produto_nome = request.GET.get('produto', '').strip()
    data_venda = request.GET.get('data', '').strip()

    vendas = Venda.objects.select_related('cliente', 'produto').order_by('-data_venda')
    if cliente_nome:
        vendas = vendas.filter(
            Q(cliente__nome__icontains=cliente_nome) | Q(cliente_nome_legado__icontains=cliente_nome)
        )
    if produto_nome:
        vendas = vendas.filter(produto__nome__icontains=produto_nome)
    if data_venda:
        try:
            data_venda_dt = datetime.strptime(data_venda, '%Y-%m-%d').date()
            vendas = vendas.filter(data_venda=data_venda_dt)
        except ValueError:
            pass

    vistos = set()
    notas = []
    for venda in vendas:
        chave = (
            venda.cliente.id if venda.cliente else venda.cliente_nome_legado,
            venda.produto.id,
            venda.quantidade_vendida,
            float(venda.preco_venda_unitario),
            float(venda.valor_total),
            venda.data_venda
        )
        if chave in vistos:
            continue
        vistos.add(chave)
        notas.append({
            'cliente_id': venda.cliente.id if venda.cliente else None,
            'cliente_nome': venda.cliente.nome if venda.cliente else venda.cliente_nome_legado,
            'produto_id': venda.produto.id,
            'produto_nome': venda.produto.nome,
            'quantidade': venda.quantidade_vendida,
            'valor_unitario': float(venda.preco_venda_unitario),
            'valor_total': float(venda.valor_total),
            'data_venda': venda.data_venda,
            'transacao_id': venda.transacao_id,
        })

    clientes_lista = list(Venda.objects.values_list('cliente__nome', flat=True).distinct())
    produtos_lista = list(Venda.objects.values_list('produto__nome', flat=True).distinct())

    context = {
        'notas': notas,
        'clientes_lista': [c for c in clientes_lista if c],
        'produtos_lista': [p for p in produtos_lista if p],
        'cliente_nome': cliente_nome,
        'produto_nome': produto_nome,
        'data_venda': data_venda,
    }
    return render(request, 'vendas/emitir_nota_fiscal.html', context)


# ========================= CLIENTES E COBRANÃ‡A =========================

@login_required
@vendedor_ou_admin
def gestao_clientes(request):
    """View para gestÃ£o de clientes"""
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    search = request.GET.get('search', '')
    if search:
        clientes = clientes.filter(
            Q(nome__icontains=search) |
            Q(telefone__icontains=search) |
            Q(cpf__icontains=search)
        )
    clientes_dados = []
    for cliente in clientes:
        clientes_dados.append({
            'id': cliente.id,
            'nome': cliente.nome,
            'telefone': cliente.telefone or '-',
            'cpf': cliente.cpf or '-',
            'saldo_devedor': cliente.saldo_devedor,
            'total_compras': cliente.total_compras,
            'data_cadastro': cliente.data_cadastro,
        })
    total_a_receber = sum(c['saldo_devedor'] for c in clientes_dados)
    context = {
        'clientes': clientes_dados,
        'total_clientes': clientes.count(),
        'total_a_receber': total_a_receber,
        'clientes_devedores': len([c for c in clientes_dados if c['saldo_devedor'] > 0]),
    }
    return render(request, 'vendas/gestao_clientes.html', context)


@login_required
@vendedor_ou_admin
@require_POST
def cadastrar_cliente(request):
    """View para cadastrar novo cliente"""
    nome = (request.POST.get('nome') or '').strip()
    telefone = (request.POST.get('telefone') or '').strip()
    email = (request.POST.get('email') or '').strip()
    cpf = (request.POST.get('cpf') or '').strip()
    endereco = (request.POST.get('endereco') or '').strip()

    if not nome:
        messages.error(request, 'Nome do cliente Ã© obrigatÃ³rio!')
        return HttpResponseRedirect(reverse('vendas:gestao_clientes'))

    try:
        Cliente.objects.create(
            nome=nome,
            telefone=telefone or None,
            email=email or None,
            cpf=cpf or None,
            endereco=endereco or None,
        )
        messages.success(request, f'Cliente "{nome}" cadastrado com sucesso!')
    except IntegrityError:
        messages.error(
            request,
            'NÃ£o foi possÃ­vel cadastrar cliente. Verifique se CPF e cÃ³digo nÃ£o estÃ£o duplicados.',
        )

    return HttpResponseRedirect(reverse('vendas:gestao_clientes'))


@login_required
@vendedor_ou_admin
def editar_cliente(request, cliente_id):
    """View para editar cliente"""
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('vendas:gestao_clientes'))

    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.nome = (request.POST.get('nome') or '').strip()
    if not cliente.nome:
        messages.error(request, 'Nome do cliente Ã© obrigatÃ³rio!')
        return HttpResponseRedirect(reverse('vendas:gestao_clientes'))

    cliente.telefone = (request.POST.get('telefone') or '').strip() or None
    cliente.email = (request.POST.get('email') or '').strip() or None
    cliente.cpf = (request.POST.get('cpf') or '').strip() or None
    cliente.endereco = (request.POST.get('endereco') or '').strip() or None
    try:
        cliente.save()
        messages.success(request, f'Cliente "{cliente.nome}" atualizado com sucesso!')
    except IntegrityError:
        messages.error(
            request,
            'NÃ£o foi possÃ­vel atualizar cliente. Verifique se CPF e cÃ³digo nÃ£o estÃ£o duplicados.',
        )

    return HttpResponseRedirect(reverse('vendas:gestao_clientes'))


@login_required
@vendedor_ou_admin
@require_POST
def deletar_cliente(request, cliente_id):
    """View para deletar (desativar) cliente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente.saldo_devedor > 0:
        messages.error(request, f'NÃ£o Ã© possÃ­vel deletar "{cliente.nome}" pois possui R$ {cliente.saldo_devedor:.2f} em dÃ­vidas pendentes!')
        return HttpResponseRedirect(reverse('vendas:gestao_clientes'))
    cliente.ativo = False
    cliente.save()
    messages.success(request, f'Cliente "{cliente.nome}" removido com sucesso!')
    return HttpResponseRedirect(reverse('vendas:gestao_clientes'))


@login_required
@vendedor_ou_admin
def tela_cobranca(request, cliente_id=None):
    """View para tela de cobranÃ§a/recebimento"""
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    cliente_selecionado = None
    vendas_pendentes = []
    historico_pagamentos = []
    pendencias_gerenciadas_contas = 0
    if cliente_id:
        cliente_selecionado = get_object_or_404(Cliente, id=cliente_id)
        contas_abertas = list(
            ContaReceber.objects.filter(
                cliente=cliente_selecionado,
                status__in=['pendente', 'parcial', 'atrasado'],
            ).values('venda_id', 'transacao_id')
        )
        venda_ids_gerenciadas = {conta['venda_id'] for conta in contas_abertas if conta['venda_id']}
        transacoes_gerenciadas = {conta['transacao_id'] for conta in contas_abertas if conta['transacao_id']}

        vendas_pendentes_qs = (
            Venda.objects.filter(
                cliente=cliente_selecionado,
                status_pagamento__in=['Pendente', 'Parcial']
            )
            .select_related('produto')
            .order_by('data_venda')
        )
        for venda in vendas_pendentes_qs:
            gerenciada_por_conta = (
                venda.id in venda_ids_gerenciadas
                or (venda.transacao_id and venda.transacao_id in transacoes_gerenciadas)
            )
            if gerenciada_por_conta:
                pendencias_gerenciadas_contas += 1
                continue
            vendas_pendentes.append(venda)

        historico_pagamentos = Pagamento.objects.filter(
            cliente=cliente_selecionado
        ).order_by('-data_pagamento')[:10]
    context = {
        'clientes': clientes,
        'cliente_selecionado': cliente_selecionado,
        'vendas_pendentes': vendas_pendentes,
        'historico_pagamentos': historico_pagamentos,
        'pendencias_gerenciadas_contas': pendencias_gerenciadas_contas,
    }
    return render(request, 'vendas/tela_cobranca.html', context)


@login_required
@vendedor_ou_admin
@require_POST
def registrar_pagamento(request):
    """View para registrar um novo pagamento"""
    cliente_id = request.POST.get('cliente_id')
    valor_pago_raw = request.POST.get('valor_pago')
    forma_pagamento = request.POST.get('forma_pagamento')
    data_pagamento = request.POST.get('data_pagamento')
    observacoes = request.POST.get('observacoes')
    venda_id = request.POST.get('venda_id')

    redirect_url = (
        reverse('vendas:tela_cobranca_cliente', kwargs={'cliente_id': cliente_id})
        if cliente_id
        else reverse('vendas:tela_cobranca')
    )

    if not all([cliente_id, valor_pago_raw, forma_pagamento, data_pagamento]):
        messages.error(request, 'Preencha todos os campos obrigatÃ³rios!')
        return HttpResponseRedirect(redirect_url)

    try:
        cliente = get_object_or_404(Cliente, id=cliente_id)
        valor_pago = _parse_positive_decimal(valor_pago_raw, 'Valor pago')
        forma_pagamento_normalizada = _normalizar_forma_pagamento(forma_pagamento)

        try:
            data_pag = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
        except ValueError:
            data_pag = date.today()

        with transaction.atomic():
            contas_abertas = list(
                ContaReceber.objects.select_for_update().filter(
                    cliente=cliente,
                    status__in=['pendente', 'parcial', 'atrasado'],
                )
            )
            venda_ids_gerenciadas = {conta.venda_id for conta in contas_abertas if conta.venda_id}
            transacoes_gerenciadas = {conta.transacao_id for conta in contas_abertas if conta.transacao_id}

            if venda_id:
                venda = get_object_or_404(Venda.objects.select_for_update(), id=venda_id)
                if venda.cliente_id != cliente.id:
                    messages.error(request, 'A venda selecionada nÃ£o pertence ao cliente informado.')
                    return HttpResponseRedirect(redirect_url)
                if venda.status_pagamento not in {'Pendente', 'Parcial'} or venda.valor_pendente <= 0:
                    messages.error(request, 'A venda selecionada nÃ£o possui saldo pendente.')
                    return HttpResponseRedirect(redirect_url)

                if (
                    venda.id in venda_ids_gerenciadas
                    or (venda.transacao_id and venda.transacao_id in transacoes_gerenciadas)
                ):
                    messages.error(
                        request,
                        'Esta venda estÃ¡ vinculada a uma conta a receber. '
                        'Registre o recebimento na tela "Contas a Receber" para manter a consistÃªncia financeira.'
                    )
                    return HttpResponseRedirect(redirect_url)

                if valor_pago > venda.valor_pendente:
                    messages.error(
                        request,
                        f'Valor informado (R$ {valor_pago:.2f}) Ã© maior que o saldo pendente da venda (R$ {venda.valor_pendente:.2f}).'
                    )
                    return HttpResponseRedirect(redirect_url)

                Pagamento.objects.create(
                    cliente=cliente,
                    venda=venda,
                    valor_pago=valor_pago,
                    forma_pagamento=forma_pagamento_normalizada,
                    data_pagamento=data_pag,
                    observacoes=observacoes,
                )
                messages.success(
                    request,
                    f'Pagamento de R$ {valor_pago:.2f} registrado com sucesso para a venda #{venda.id}!'
                )
                return HttpResponseRedirect(redirect_url)

            vendas_pendentes = list(
                Venda.objects.select_for_update()
                .filter(cliente=cliente, status_pagamento__in=['Pendente', 'Parcial'])
                .order_by('data_venda', 'id')
            )
            if not vendas_pendentes:
                messages.error(request, 'Cliente sem vendas pendentes para recebimento.')
                return HttpResponseRedirect(redirect_url)

            vendas_disponiveis = []
            vendas_bloqueadas = 0
            for venda_pendente in vendas_pendentes:
                gerenciada_por_conta = (
                    venda_pendente.id in venda_ids_gerenciadas
                    or (
                        venda_pendente.transacao_id
                        and venda_pendente.transacao_id in transacoes_gerenciadas
                    )
                )
                if gerenciada_por_conta:
                    vendas_bloqueadas += 1
                    continue
                vendas_disponiveis.append(venda_pendente)

            if not vendas_disponiveis:
                messages.error(
                    request,
                    'As pendÃªncias deste cliente estÃ£o vinculadas a contas a receber. '
                    'Use a tela "Contas a Receber" para registrar o pagamento.'
                )
                return HttpResponseRedirect(redirect_url)

            total_pendente_disponivel = sum(
                (venda_pendente.valor_pendente for venda_pendente in vendas_disponiveis),
                Decimal('0'),
            )
            if valor_pago > total_pendente_disponivel:
                messages.error(
                    request,
                    f'Valor informado (R$ {valor_pago:.2f}) excede o saldo pendente disponÃ­vel (R$ {total_pendente_disponivel:.2f}).'
                )
                return HttpResponseRedirect(redirect_url)

            valor_restante = valor_pago
            pagamentos_gerados = 0
            for venda_pendente in vendas_disponiveis:
                if valor_restante <= 0:
                    break
                pendente = venda_pendente.valor_pendente
                if pendente <= 0:
                    continue
                valor_a_pagar = min(valor_restante, pendente)
                Pagamento.objects.create(
                    cliente=cliente,
                    venda=venda_pendente,
                    valor_pago=valor_a_pagar,
                    forma_pagamento=forma_pagamento_normalizada,
                    data_pagamento=data_pag,
                    observacoes=observacoes,
                )
                valor_restante -= valor_a_pagar
                pagamentos_gerados += 1

            if valor_restante > 0:
                raise ValueError('NÃ£o foi possÃ­vel alocar integralmente o pagamento nas vendas pendentes.')

        mensagem = f'Pagamento de R$ {valor_pago:.2f} registrado com sucesso em {pagamentos_gerados} venda(s).'
        if vendas_bloqueadas:
            mensagem += f' {vendas_bloqueadas} venda(s) vinculada(s) a contas a receber nÃ£o foram alteradas.'
        messages.success(request, mensagem)
        return HttpResponseRedirect(redirect_url)
    except ValueError as exc:
        messages.error(request, str(exc))
        return HttpResponseRedirect(redirect_url)
    except (DatabaseError, OSError) as exc:
        _log_operational_error(
            'registrar_pagamento',
            request,
            exc,
            cliente_id=cliente_id,
            venda_id=venda_id,
        )
        messages.error(request, 'Erro ao registrar pagamento.')
        return HttpResponseRedirect(redirect_url)


@login_required
@vendedor_ou_admin
def detalhes_cliente(request, cliente_id):
    """View para ver detalhes completos do cliente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    vendas = Venda.objects.filter(cliente=cliente).order_by('-data_venda')
    pagamentos = Pagamento.objects.filter(cliente=cliente).order_by('-data_pagamento')
    total_comprado = sum(v.valor_total for v in vendas)
    total_pago = sum(p.valor_pago for p in pagamentos)
    context = {
        'cliente': cliente,
        'vendas': vendas,
        'pagamentos': pagamentos,
        'total_comprado': total_comprado,
        'total_pago': total_pago,
    }
    return render(request, 'vendas/detalhes_cliente.html', context)


# ========================= GESTÃƒO DE VENDAS =========================

@login_required
@vendedor_ou_admin
def gestao_vendas(request):
    """View para listagem de vendas consolidada por cliente e mÃªs."""
    produtos_disponiveis = Produto.objects.filter(estoque_atual__gt=0).order_by('nome')
    formas_pagamento_padrao = [label for _, label in Pagamento.FORMAS_PAGAMENTO]
    formas_pagamento_registradas = list(
        Venda.objects
        .exclude(forma_pagamento_legado__isnull=True)
        .exclude(forma_pagamento_legado='')
        .values_list('forma_pagamento_legado', flat=True)
        .distinct()
    )
    tipos_pagamento_disponiveis = sorted(
        {str(item).strip() for item in (formas_pagamento_padrao + formas_pagamento_registradas) if str(item).strip()},
        key=lambda valor: valor.lower(),
    )

    vendas_agrupadas = []
    vendas_consolidadas = []
    todas_vendas = (
        Venda.objects
        .all()
        .select_related('produto', 'produto__categoria', 'cliente')
        .order_by('-data_venda', '-id')
    )

    mes = (request.GET.get('mes') or '').strip()
    if mes:
        try:
            ano, mes_num = mes.split('-')
            todas_vendas = todas_vendas.filter(data_venda__month=mes_num, data_venda__year=ano)
        except ValueError:
            pass

    produto_id = (request.GET.get('produto') or '').strip()
    if produto_id:
        todas_vendas = todas_vendas.filter(produto_id=produto_id)

    cliente_selecionado = (request.GET.get('cliente') or '').strip()
    if cliente_selecionado:
        todas_vendas = todas_vendas.filter(
            Q(cliente__nome__icontains=cliente_selecionado)
            | Q(cliente__codigo__icontains=cliente_selecionado)
            | Q(cliente_nome_legado__icontains=cliente_selecionado)
        )

    tipo_pagamento_selecionado = (request.GET.get('tipo_pagamento') or '').strip()
    if tipo_pagamento_selecionado:
        todas_vendas = todas_vendas.filter(forma_pagamento_legado__iexact=tipo_pagamento_selecionado)

    vendas_filtradas = list(todas_vendas)
    transacoes_map = {}

    for venda in vendas_filtradas:
        transacao_id = venda.transacao_id or f"legacy_{venda.id}"
        bucket = transacoes_map.get(transacao_id)
        if not bucket:
            bucket = {
                'transacao_id': transacao_id,
                'vendas': [],
                'formas_pagamento': set(),
                'status_pagamento': set(),
            }
            transacoes_map[transacao_id] = bucket

        bucket['vendas'].append(venda)
        bucket['formas_pagamento'].add((venda.forma_pagamento_legado or '').strip() or 'Pago')
        bucket['status_pagamento'].add((venda.status_pagamento or '').strip() or 'Pago')

    for transacao_id, bucket in transacoes_map.items():
        vendas_transacao = bucket['vendas']
        venda_principal = vendas_transacao[0]

        total_valor = sum((v.valor_total for v in vendas_transacao), Decimal('0'))
        total_lucro = sum((v.lucro for v in vendas_transacao), Decimal('0'))
        total_itens = sum(v.quantidade_vendida for v in vendas_transacao)
        forma_pagamento = (
            next(iter(bucket['formas_pagamento']))
            if len(bucket['formas_pagamento']) == 1
            else 'MÃºltiplos'
        )
        status_pagamento = _consolidar_status_pagamento(bucket['status_pagamento'])

        produtos_detalhes = []
        for item in vendas_transacao:
            categoria_nome = (
                item.produto.categoria.nome
                if item.produto and item.produto.categoria
                else 'Categoria nÃ£o cadastrada'
            )
            preco_original_unitario = (
                item.preco_original_unitario
                if item.preco_original_unitario
                else (
                    item.produto.preco_venda_sugerido
                    if item.produto and item.produto.preco_venda_sugerido is not None
                    else item.preco_venda_unitario
                )
            )
            subtotal_original = (
                Decimal(str(preco_original_unitario)) * Decimal(str(item.quantidade_vendida))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            desconto_valor = Decimal(str(item.desconto_valor_total or 0)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP,
            )
            desconto_percentual = Decimal(str(item.desconto_percentual or 0)).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP,
            )
            produtos_detalhes.append({
                'produto_id': item.produto_id,
                'nome': item.produto.nome,
                'categoria': categoria_nome,
                'quantidade': item.quantidade_vendida,
                'preco_original_unitario': float(preco_original_unitario),
                'preco_unitario': float(item.preco_venda_unitario),
                'desconto_valor': float(desconto_valor),
                'desconto_percentual': float(desconto_percentual),
                'subtotal_original': float(subtotal_original),
                'subtotal': float(item.valor_total),
            })

        produtos_str = ", ".join(
            [f"{item.produto.nome} ({item.quantidade_vendida}x)" for item in vendas_transacao]
        )

        vendas_agrupadas.append({
            'transacao_id': transacao_id,
            'data_venda': venda_principal.data_venda,
            'produtos': produtos_str,
            'produtos_lista': vendas_transacao,
            'produtos_detalhes': produtos_detalhes,
            'total_itens': total_itens,
            'total_valor': total_valor,
            'total_lucro': total_lucro,
            'cliente': venda_principal.cliente,
            'cliente_nome_legado': venda_principal.cliente_nome_legado,
            'forma_pagamento': forma_pagamento,
            'status_pagamento': status_pagamento,
            'venda_principal': venda_principal,
        })

    grupos_consolidados = {}
    for venda in vendas_agrupadas:
        data_ref = venda['data_venda']
        periodo_data = date(data_ref.year, data_ref.month, 1)

        cliente_obj = venda.get('cliente')
        cliente_nome_legado = (venda.get('cliente_nome_legado') or '').strip()
        if cliente_obj and cliente_obj.id:
            cliente_group_key = f"cliente:{cliente_obj.id}"
        else:
            cliente_group_key = f"legado:{cliente_nome_legado.lower() or 'sem-cliente'}"

        group_key = (cliente_group_key, periodo_data)
        consolidado = grupos_consolidados.get(group_key)
        if not consolidado:
            consolidado = {
                'periodo_data': periodo_data,
                'periodo_label': periodo_data.strftime('%m/%Y'),
                'cliente': cliente_obj,
                'cliente_nome_legado': cliente_nome_legado,
                'cliente_nome': (
                    cliente_obj.nome if cliente_obj and cliente_obj.nome
                    else (cliente_nome_legado or 'Cliente nÃ£o informado')
                ),
                'cliente_codigo': cliente_obj.codigo if cliente_obj and cliente_obj.codigo else '',
                'total_itens': 0,
                'total_valor': Decimal('0'),
                'total_lucro': Decimal('0'),
                'formas_pagamento': set(),
                'status_pagamento': set(),
                'compras': [],
            }
            grupos_consolidados[group_key] = consolidado

        consolidado['total_itens'] += venda['total_itens']
        consolidado['total_valor'] += Decimal(str(venda['total_valor']))
        consolidado['total_lucro'] += Decimal(str(venda['total_lucro']))
        consolidado['formas_pagamento'].add((venda.get('forma_pagamento') or '').strip() or 'Pago')
        consolidado['status_pagamento'].add((venda.get('status_pagamento') or '').strip() or 'Pago')
        consolidado['compras'].append(venda)

    ordenacao_selecionada = (request.GET.get('ordenar') or '').strip()
    for index, consolidado in enumerate(grupos_consolidados.values(), start=1):
        consolidado['grupo_id'] = f"grupo_{index}"
        consolidado['quantidade_compras'] = len(consolidado['compras'])
        consolidado['data_ultima_compra'] = max(
            (item['data_venda'] for item in consolidado['compras']),
            default=consolidado['periodo_data'],
        )
        consolidado['forma_pagamento'] = (
            next(iter(consolidado['formas_pagamento']))
            if len(consolidado['formas_pagamento']) == 1
            else 'MÃºltiplos'
        )
        consolidado['status'] = _consolidar_status_pagamento(consolidado['status_pagamento'])
        consolidado['compras'] = sorted(
            consolidado['compras'],
            key=lambda item: (item['data_venda'], item['transacao_id']),
            reverse=True,
        )
        consolidado.pop('formas_pagamento', None)
        consolidado.pop('status_pagamento', None)

    vendas_consolidadas = list(grupos_consolidados.values())
    if ordenacao_selecionada == 'maior_valor':
        vendas_consolidadas.sort(
            key=lambda item: (
                item['total_valor'],
                item['data_ultima_compra'],
                item['periodo_data'],
                item['cliente_nome'].lower(),
            ),
            reverse=True,
        )
    elif ordenacao_selecionada == 'maior_quantidade':
        vendas_consolidadas.sort(
            key=lambda item: (
                item['total_itens'],
                item['data_ultima_compra'],
                item['periodo_data'],
                item['cliente_nome'].lower(),
            ),
            reverse=True,
        )
    else:
        ordenacao_selecionada = ''
        vendas_consolidadas.sort(
            key=lambda item: (
                item['data_ultima_compra'],
                item['periodo_data'],
                item['cliente_nome'].lower(),
            ),
            reverse=True,
        )

    agora_local = timezone.localtime(timezone.now())
    mes_atual = agora_local.month
    ano_atual = agora_local.year
    if mes:
        vendas_mes = Venda.objects.all()
        try:
            ano_ref, mes_ref = mes.split('-')
            vendas_mes = vendas_mes.filter(data_venda__year=int(ano_ref), data_venda__month=int(mes_ref))
        except (TypeError, ValueError):
            vendas_mes = Venda.objects.filter(data_venda__month=mes_atual, data_venda__year=ano_atual)
    else:
        vendas_mes = Venda.objects.filter(data_venda__month=mes_atual, data_venda__year=ano_atual)
    if produto_id:
        vendas_mes = vendas_mes.filter(produto_id=produto_id)
    if cliente_selecionado:
        vendas_mes = vendas_mes.filter(
            Q(cliente__nome__icontains=cliente_selecionado)
            | Q(cliente__codigo__icontains=cliente_selecionado)
            | Q(cliente_nome_legado__icontains=cliente_selecionado)
        )
    if tipo_pagamento_selecionado:
        vendas_mes = vendas_mes.filter(forma_pagamento_legado__iexact=tipo_pagamento_selecionado)

    faturamento_mes = sum(venda.valor_total for venda in vendas_mes)
    lucro_mes = sum(venda.lucro for venda in vendas_mes)

    transacoes_unicas_mes = vendas_mes.values('transacao_id').distinct().count()
    vendas_sem_transacao = vendas_mes.filter(transacao_id__isnull=True).count()
    total_vendas_mes = transacoes_unicas_mes + vendas_sem_transacao

    ticket_medio = faturamento_mes / total_vendas_mes if total_vendas_mes > 0 else 0

    # === Resumo de vendas fiado (cards + modal clicÃ¡vel) ===
    contas_fiado_qs = (
        ContaReceber.objects
        .filter(origem='fiado')
        .select_related('cliente')
        .prefetch_related('recebimentos')
        .order_by('-criado_em', '-id')
    )
    if mes:
        try:
            ano_ref, mes_ref = mes.split('-')
            contas_fiado_qs = contas_fiado_qs.filter(
                criado_em__year=int(ano_ref),
                criado_em__month=int(mes_ref),
            )
        except ValueError:
            pass

    contas_fiado = list(contas_fiado_qs)
    total_lancado_fiado = Decimal('0')
    total_recebido_fiado = Decimal('0')
    saldo_aberto_fiado = Decimal('0')
    contas_ativas_fiado = []
    clientes_saldo_fiado = {}
    eventos_recebimento_fiado = []

    for conta in contas_fiado:
        if conta.status == 'cancelado':
            continue

        total_lancado_fiado += Decimal(str(conta.valor))
        total_recebido_fiado += conta.total_recebido
        saldo_aberto_fiado += conta.saldo_aberto

        if conta.saldo_aberto > 0 and conta.status in {'pendente', 'parcial', 'atrasado'}:
            contas_ativas_fiado.append(conta)
            consolidado_cliente = clientes_saldo_fiado.get(conta.cliente_id)
            if not consolidado_cliente:
                consolidado_cliente = {
                    'cliente_nome': conta.cliente.nome,
                    'saldo': Decimal('0'),
                    'contas': 0,
                    'proximo_vencimento': conta.data_vencimento,
                }
                clientes_saldo_fiado[conta.cliente_id] = consolidado_cliente

            consolidado_cliente['saldo'] += conta.saldo_aberto
            consolidado_cliente['contas'] += 1
            if conta.data_vencimento < consolidado_cliente['proximo_vencimento']:
                consolidado_cliente['proximo_vencimento'] = conta.data_vencimento

        for recebimento in conta.recebimentos.all():
            eventos_recebimento_fiado.append({
                'ordem_data': recebimento.data_recebimento,
                'ordem_criado': recebimento.criado_em,
                'titulo': conta.cliente.nome,
                'descricao': (
                    f'Conta #{conta.id} â€¢ {recebimento.forma_pagamento} â€¢ '
                    f'{recebimento.data_recebimento.strftime("%d/%m/%Y")}'
                ),
                'valor': float(recebimento.valor),
                'tag': 'Recebimento',
            })

    def _currency_br(valor):
        return _format_currency_br(valor)

    def _nome_cliente_venda(venda_dict):
        cliente_obj = venda_dict.get('cliente')
        if cliente_obj and getattr(cliente_obj, 'nome', None):
            return cliente_obj.nome
        return venda_dict.get('cliente_nome_legado') or 'Cliente nÃ£o informado'

    contas_ativas_fiado_ordenadas = sorted(
        contas_ativas_fiado,
        key=lambda c: (c.data_vencimento, c.id),
    )[:8]
    itens_card_ativas = [
        {
            'titulo': conta.cliente.nome,
            'descricao': f'Conta #{conta.id} â€¢ vencimento {conta.data_vencimento.strftime("%d/%m/%Y")}',
            'valor': _currency_br(conta.saldo_aberto),
            'tag': conta.get_status_display(),
        }
        for conta in contas_ativas_fiado_ordenadas
    ]

    itens_card_lancado = []
    for conta in contas_fiado:
        if conta.status == 'cancelado':
            continue
        itens_card_lancado.append({
            'titulo': conta.cliente.nome,
            'descricao': f'Conta #{conta.id} â€¢ lanÃ§amento em {conta.criado_em.strftime("%d/%m/%Y %H:%M")}',
            'valor': _currency_br(conta.valor),
            'tag': conta.get_status_display(),
        })
        if len(itens_card_lancado) >= 8:
            break

    eventos_recebimento_fiado.sort(
        key=lambda item: (item['ordem_data'], item['ordem_criado']),
        reverse=True,
    )
    itens_card_recebido = [
        {
            'titulo': item['titulo'],
            'descricao': item['descricao'],
            'valor': _currency_br(item['valor']),
            'tag': item['tag'],
        }
        for item in eventos_recebimento_fiado[:8]
    ]

    clientes_devedores = sorted(
        clientes_saldo_fiado.values(),
        key=lambda item: item['saldo'],
        reverse=True,
    )[:8]
    itens_card_saldo = [
        {
            'titulo': item['cliente_nome'],
            'descricao': (
                f'{item["contas"]} conta(s) em aberto â€¢ prÃ³ximo vencimento '
                f'{item["proximo_vencimento"].strftime("%d/%m/%Y")}'
            ),
            'valor': _currency_br(item['saldo']),
            'tag': 'Saldo em aberto',
        }
        for item in clientes_devedores
    ]

    vendas_ordenadas = sorted(
        vendas_agrupadas,
        key=lambda item: (item['data_venda'], item['transacao_id']),
        reverse=True,
    )
    itens_card_total_vendas = [
        {
            'titulo': _nome_cliente_venda(venda),
            'descricao': (
                f'{venda["total_itens"]} item(ns) â€¢ '
                f'{venda["data_venda"].strftime("%d/%m/%Y")}'
            ),
            'valor': _currency_br(venda['total_valor']),
            'tag': venda.get('forma_pagamento') or 'Pago',
        }
        for venda in vendas_ordenadas[:8]
    ]

    vendas_por_faturamento = sorted(
        vendas_agrupadas,
        key=lambda item: item['total_valor'],
        reverse=True,
    )
    itens_card_faturamento = [
        {
            'titulo': _nome_cliente_venda(venda),
            'descricao': venda['produtos'][:90],
            'valor': _currency_br(venda['total_valor']),
            'tag': f'{venda["total_itens"]} item(ns)',
        }
        for venda in vendas_por_faturamento[:8]
    ]

    vendas_por_lucro = sorted(
        vendas_agrupadas,
        key=lambda item: item['total_lucro'],
        reverse=True,
    )
    itens_card_lucro = [
        {
            'titulo': _nome_cliente_venda(venda),
            'descricao': venda['produtos'][:90],
            'valor': _currency_br(venda['total_lucro']),
            'tag': f'{venda["total_itens"]} item(ns)',
        }
        for venda in vendas_por_lucro[:8]
    ]

    vendas_por_ticket = sorted(
        vendas_agrupadas,
        key=lambda item: (
            (Decimal(str(item['total_valor'])) / max(item['total_itens'], 1)),
            item['transacao_id'],
        ),
        reverse=True,
    )
    itens_card_ticket = [
        {
            'titulo': _nome_cliente_venda(venda),
            'descricao': (
                f'{venda["total_itens"]} item(ns) â€¢ '
                f'{venda["data_venda"].strftime("%d/%m/%Y")}'
            ),
            'valor': _currency_br(
                Decimal(str(venda['total_valor'])) / Decimal(str(max(venda['total_itens'], 1)))
            ),
            'tag': 'Ticket da venda',
        }
        for venda in vendas_por_ticket[:8]
    ]

    fiado_cards_payload = {
        'total_vendas': {
            'titulo': 'Total de vendas',
            'descricao': 'Ãšltimas vendas registradas no perÃ­odo filtrado.',
            'valor': f'{total_vendas_mes} venda(s)',
            'vazio': 'Nenhuma venda encontrada para o perÃ­odo selecionado.',
            'itens': itens_card_total_vendas,
        },
        'faturamento': {
            'titulo': 'Faturamento do mÃªs',
            'descricao': 'Vendas com maior valor total no perÃ­odo.',
            'valor': _currency_br(faturamento_mes),
            'vazio': 'Nenhuma venda encontrada para compor o faturamento.',
            'itens': itens_card_faturamento,
        },
        'lucro': {
            'titulo': 'Lucro do mÃªs',
            'descricao': 'Vendas com maior lucro no perÃ­odo.',
            'valor': _currency_br(lucro_mes),
            'vazio': 'Nenhuma venda encontrada para compor o lucro.',
            'itens': itens_card_lucro,
        },
        'ticket': {
            'titulo': 'Ticket mÃ©dio',
            'descricao': 'Vendas com maior ticket por item no perÃ­odo.',
            'valor': _currency_br(ticket_medio),
            'vazio': 'Sem dados para cÃ¡lculo de ticket mÃ©dio.',
            'itens': itens_card_ticket,
        },
        'ativas': {
            'titulo': 'Contas fiado ativas',
            'descricao': 'Contas fiado com saldo em aberto.',
            'valor': f'{len(contas_ativas_fiado)} conta(s)',
            'vazio': 'Nenhuma conta fiado ativa para o perÃ­odo selecionado.',
            'itens': itens_card_ativas,
        },
        'lancado': {
            'titulo': 'Total lanÃ§ado no fiado',
            'descricao': 'Ãšltimos lanÃ§amentos de vendas fiado.',
            'valor': _currency_br(total_lancado_fiado),
            'vazio': 'Nenhum lanÃ§amento de fiado encontrado.',
            'itens': itens_card_lancado,
        },
        'recebido': {
            'titulo': 'Total recebido do fiado',
            'descricao': 'Ãšltimos recebimentos vinculados a contas fiado.',
            'valor': _currency_br(total_recebido_fiado),
            'vazio': 'Nenhum recebimento de fiado registrado.',
            'itens': itens_card_recebido,
        },
        'saldo': {
            'titulo': 'Saldo em aberto do fiado',
            'descricao': 'Clientes com maior saldo fiado em aberto.',
            'valor': _currency_br(saldo_aberto_fiado),
            'vazio': 'Nenhum saldo fiado em aberto.',
            'itens': itens_card_saldo,
        },
    }

    paginator = Paginator(vendas_consolidadas, 10)
    page_number = request.GET.get('page')
    vendas_paginadas = paginator.get_page(page_number)

    vendas_data_payload = {}
    for grupo in vendas_paginadas.object_list:
        for compra in grupo.get('compras', []):
            transacao_id = compra.get('transacao_id')
            if not transacao_id:
                continue

            cliente_obj = compra.get('cliente')
            cliente_nome = (
                cliente_obj.nome if cliente_obj and cliente_obj.nome
                else (compra.get('cliente_nome_legado') or 'NÃ£o informado')
            )
            cliente_codigo = cliente_obj.codigo if cliente_obj and cliente_obj.codigo else ''

            vendas_data_payload[transacao_id] = {
                'data': compra['data_venda'].strftime('%d/%m/%Y'),
                'dataIso': compra['data_venda'].strftime('%Y-%m-%d'),
                'cliente': cliente_nome,
                'codigo': cliente_codigo,
                'pagamento': compra.get('forma_pagamento') or 'Pago',
                'total': float(Decimal(str(compra.get('total_valor') or 0))),
                'lucro': float(Decimal(str(compra.get('total_lucro') or 0))),
                'produtos': [
                    {
                        'nome': produto['nome'],
                        'categoria': produto['categoria'],
                        'produtoId': int(produto.get('produto_id') or 0),
                        'quantidade': int(produto['quantidade']),
                        'precoOriginalUnitario': float(produto.get('preco_original_unitario') or produto['preco_unitario']),
                        'precoUnitario': float(produto['preco_unitario']),
                        'descontoValor': float(produto.get('desconto_valor') or 0),
                        'descontoPercentual': float(produto.get('desconto_percentual') or 0),
                        'subtotalOriginal': float(produto.get('subtotal_original') or produto['subtotal']),
                        'subtotal': float(produto['subtotal']),
                    }
                    for produto in compra.get('produtos_detalhes', [])
                ],
            }

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_string = query_params.urlencode()
    export_query_params = request.GET.copy()
    export_query_params.pop('page', None)
    export_query_string = export_query_params.urlencode()

    context = {
        'vendas': vendas_paginadas,
        'produtos': produtos_disponiveis,
        'produtos_disponiveis': produtos_disponiveis,
        'tipos_pagamento_disponiveis': tipos_pagamento_disponiveis,
        'mes_selecionado': mes,
        'produto_selecionado': produto_id,
        'cliente_selecionado': cliente_selecionado,
        'tipo_pagamento_selecionado': tipo_pagamento_selecionado,
        'ordenacao_selecionada': ordenacao_selecionada,
        'filtros_ativos': bool(
            mes
            or produto_id
            or cliente_selecionado
            or tipo_pagamento_selecionado
            or ordenacao_selecionada
        ),
        'faturamento_mes': faturamento_mes,
        'lucro_mes': lucro_mes,
        'total_vendas_mes': total_vendas_mes,
        'ticket_medio': ticket_medio,
        'fiado_total_contas_ativas': len(contas_ativas_fiado),
        'fiado_total_lancado': total_lancado_fiado,
        'fiado_total_recebido': total_recebido_fiado,
        'fiado_saldo_aberto': saldo_aberto_fiado,
        'fiado_cards_payload': fiado_cards_payload,
        'query_string': query_string,
        'export_query_string': export_query_string,
        'ultima_atualizacao': agora_local,
        'vendas_data_payload': vendas_data_payload,
    }
    return render(request, 'vendas/gestao_de_vendas.html', context)


@login_required
@vendedor_ou_admin
@require_POST
def registrar_venda(request):
    """View para registrar venda - Suporta mÃºltiplos produtos"""
    try:
        carrinho_json = request.POST.get('carrinho_json')
        if not carrinho_json:
            messages.error(request, 'Carrinho vazio! Adicione produtos antes de finalizar.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

        carrinho = json.loads(carrinho_json)
        if not carrinho:
            messages.error(request, 'Carrinho vazio! Adicione produtos antes de finalizar.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

        data_venda = request.POST.get('data_venda')
        cliente_nome = ' '.join((request.POST.get('cliente') or '').split())
        forma_pagamento = (request.POST.get('forma_pagamento') or '').strip()

        if not data_venda or not forma_pagamento:
            messages.error(request, 'Preencha data da venda e forma de pagamento.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

        if not cliente_nome:
            messages.error(request, 'Informe o nome do cliente para registrar a venda.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))
        if len(cliente_nome) < 2:
            messages.error(request, 'Informe um nome de cliente vÃ¡lido.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))
        if len(cliente_nome) > 255:
            messages.error(request, 'Nome do cliente deve ter no mÃ¡ximo 255 caracteres.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

        try:
            datetime.strptime(data_venda, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Data da venda invÃ¡lida.')
            return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

        carrinho_validado = []
        for item in carrinho:
            produto_id = _parse_positive_int(item.get('id'), 'Produto')
            quantidade = _parse_positive_int(item.get('quantidade'), 'Quantidade')
            preco_unitario_original = _parse_positive_decimal(
                item.get('precoUnitarioOriginal', item.get('precoUnitario')),
                'PreÃ§o unitÃ¡rio',
            )
            try:
                desconto_valor = Decimal(str(item.get('descontoValor', 0) or 0))
                desconto_percentual = Decimal(str(item.get('descontoPercentual', 0) or 0))
            except (InvalidOperation, TypeError, ValueError):
                raise ValueError('Desconto invÃ¡lido no carrinho.')

            desconto_valor = desconto_valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            desconto_percentual = desconto_percentual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if desconto_valor < 0:
                raise ValueError('Desconto em valor nÃ£o pode ser negativo.')
            if desconto_percentual < 0:
                raise ValueError('Desconto percentual nÃ£o pode ser negativo.')
            if desconto_percentual > Decimal('100'):
                raise ValueError('Desconto percentual nÃ£o pode ser maior que 100%.')

            subtotal_original = (
                preco_unitario_original * Decimal(str(quantidade))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if desconto_valor > subtotal_original:
                raise ValueError('Desconto nÃ£o pode ser maior que o valor total do produto no carrinho.')

            subtotal_final = (
                subtotal_original - desconto_valor
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if subtotal_final <= Decimal('0'):
                raise ValueError('Desconto invÃ¡lido: o valor final do item deve ser maior que zero.')

            preco_unitario_final = (
                subtotal_final / Decimal(str(quantidade))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            subtotal_final_ajustado = (
                preco_unitario_final * Decimal(str(quantidade))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            desconto_valor_ajustado = (
                subtotal_original - subtotal_final_ajustado
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            carrinho_validado.append({
                'id': produto_id,
                'quantidade': quantidade,
                'preco_unitario_original': preco_unitario_original,
                'preco_unitario_final': preco_unitario_final,
                'desconto_valor': desconto_valor_ajustado,
                'desconto_percentual': (
                    ((desconto_valor_ajustado / subtotal_original) * Decimal('100'))
                    .quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    if subtotal_original > 0 else Decimal('0.00')
                ),
            })

        import uuid
        transacao_id = str(uuid.uuid4())[:8] + datetime.now().strftime('%Y%m%d%H%M%S')

        lucro_total = Decimal('0')
        valor_total = Decimal('0')
        economia_total = Decimal('0')
        produtos_cache = {}
        cliente_obj = None
        cliente_criado_automatico = False
        codigo_gerado_automatico = False

        with transaction.atomic():
            cliente_obj, cliente_criado_automatico, codigo_gerado_automatico = _obter_ou_criar_cliente_por_nome(
                cliente_nome
            )

            for item in carrinho_validado:
                produto = Produto.objects.select_for_update().filter(id=item['id']).first()
                if not produto:
                    raise ValueError('Produto invÃ¡lido no carrinho.')
                if produto.estoque_atual < item['quantidade']:
                    raise ValueError(
                        f'Estoque insuficiente para "{produto.nome}"! '
                        f'DisponÃ­vel: {produto.estoque_atual}, solicitado: {item["quantidade"]}.'
                    )
                produtos_cache[item['id']] = produto

            for item in carrinho_validado:
                produto = produtos_cache[item['id']]
                venda = Venda.objects.create(
                    produto=produto,
                    cliente=cliente_obj,
                    cliente_nome_legado=None,
                    quantidade_vendida=item['quantidade'],
                    preco_venda_unitario=item['preco_unitario_final'],
                    preco_original_unitario=item['preco_unitario_original'],
                    desconto_valor_total=item['desconto_valor'],
                    desconto_percentual=item['desconto_percentual'],
                    status_pagamento='Pago',
                    forma_pagamento_legado=forma_pagamento,
                    data_venda=data_venda,
                    transacao_id=transacao_id
                )

                produto.estoque_atual -= item['quantidade']
                produto.save(update_fields=['estoque_atual'])
                _registrar_movimentacao_estoque(
                    produto,
                    'saida',
                    item['quantidade'],
                    request,
                    observacao=f'SaÃ­da por venda (transaÃ§Ã£o {transacao_id})',
                )

                lucro_total += venda.lucro
                valor_total += venda.valor_total
                economia_total += item['desconto_valor']

        total_itens = sum(item['quantidade'] for item in carrinho_validado)
        mensagem_sucesso = (
            f'Venda registrada com sucesso! {len(carrinho_validado)} produto(s), {total_itens} unidade(s). '
            f'Total: R$ {valor_total:.2f} | Lucro: R$ {lucro_total:.2f}'
        )
        if economia_total > 0:
            mensagem_sucesso += f' | Descontos: R$ {economia_total:.2f}'
        messages.success(
            request,
            mensagem_sucesso
        )
        if cliente_criado_automatico and cliente_obj:
            messages.info(request, f'Cliente "{cliente_obj.nome}" foi cadastrado automaticamente.')
        elif codigo_gerado_automatico and cliente_obj:
            messages.info(request, f'CÃ³digo do cliente "{cliente_obj.nome}" foi gerado automaticamente.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    except json.JSONDecodeError:
        messages.error(request, 'Erro ao processar carrinho. Tente novamente.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))
    except ValueError as e:
        messages.error(request, f'Erro nos dados informados: {str(e)}')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))
    except (DatabaseError, OSError) as exc:
        _log_operational_error(
            'registrar_venda',
            request,
            exc,
            cliente_nome=cliente_nome,
            forma_pagamento=forma_pagamento,
        )
        messages.error(request, 'Erro ao registrar venda.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))


@login_required
@vendedor_ou_admin
@require_POST
def editar_transacao(request, transacao_id):
    """Atualiza os campos comuns (data, cliente e pagamento) de uma transaÃ§Ã£o."""
    if transacao_id.startswith('legacy_'):
        venda_id = transacao_id.replace('legacy_', '')
        vendas = Venda.objects.filter(id=venda_id)
    else:
        vendas = Venda.objects.filter(transacao_id=transacao_id)

    if not vendas.exists():
        messages.error(request, 'TransaÃ§Ã£o nÃ£o encontrada para ediÃ§Ã£o.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    data_venda_str = request.POST.get('data_venda', '').strip()
    forma_pagamento = request.POST.get('forma_pagamento', '').strip()
    cliente_nome = ' '.join((request.POST.get('cliente') or '').split())

    if not data_venda_str or not forma_pagamento:
        messages.error(request, 'Preencha a data da venda e a forma de pagamento para editar a transaÃ§Ã£o.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    try:
        nova_data_venda = datetime.strptime(data_venda_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Data invÃ¡lida para ediÃ§Ã£o da venda.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    if cliente_nome and len(cliente_nome) < 2:
        messages.error(request, 'Informe um nome de cliente vÃ¡lido para ediÃ§Ã£o.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))
    if cliente_nome and len(cliente_nome) > 255:
        messages.error(request, 'Nome do cliente deve ter no mÃ¡ximo 255 caracteres.')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    forma_pagamento_legado = None if forma_pagamento == 'Pago' else forma_pagamento
    cliente_obj = None
    cliente_criado_automatico = False
    codigo_gerado_automatico = False

    with transaction.atomic():
        if cliente_nome:
            cliente_obj, cliente_criado_automatico, codigo_gerado_automatico = _obter_ou_criar_cliente_por_nome(
                cliente_nome
            )

        for venda in vendas:
            venda.data_venda = nova_data_venda
            venda.forma_pagamento_legado = forma_pagamento_legado

            if cliente_nome:
                venda.cliente = cliente_obj
                venda.cliente_nome_legado = None
            else:
                venda.cliente = None
                venda.cliente_nome_legado = None

            venda.save(update_fields=['data_venda', 'forma_pagamento_legado', 'cliente', 'cliente_nome_legado'])

    messages.success(request, 'TransaÃ§Ã£o atualizada com sucesso!')
    if cliente_criado_automatico and cliente_obj:
        messages.info(request, f'Cliente "{cliente_obj.nome}" foi cadastrado automaticamente.')
    elif codigo_gerado_automatico and cliente_obj:
        messages.info(request, f'CÃ³digo do cliente "{cliente_obj.nome}" foi gerado automaticamente.')
    return HttpResponseRedirect(reverse('vendas:gestao_vendas'))


@login_required
@vendedor_ou_admin
@require_POST
def deletar_venda(request, venda_id):
    """View para deletar venda"""
    venda = get_object_or_404(Venda, id=venda_id)
    with transaction.atomic():
        produto = Produto.objects.select_for_update().get(id=venda.produto_id)
        produto.estoque_atual += venda.quantidade_vendida
        produto.save(update_fields=['estoque_atual'])
        _registrar_movimentacao_estoque(
            produto,
            'devolucao',
            venda.quantidade_vendida,
            request,
            observacao=f'Retorno por exclusÃ£o da venda #{venda.id}',
        )
        venda.delete()
    messages.success(request, 'Venda deletada e estoque restaurado!')
    return HttpResponseRedirect(reverse('vendas:gestao_vendas'))


@login_required
@vendedor_ou_admin
@require_POST
def deletar_transacao(request, transacao_id):
    """View para deletar todas as vendas de uma transaÃ§Ã£o"""
    if transacao_id.startswith('legacy_'):
        venda_id = transacao_id.replace('legacy_', '')
        vendas = Venda.objects.filter(id=venda_id)
    else:
        vendas = Venda.objects.filter(transacao_id=transacao_id)

    if not vendas.exists():
        messages.error(request, 'Venda nÃ£o encontrada!')
        return HttpResponseRedirect(reverse('vendas:gestao_vendas'))

    total_itens = 0
    with transaction.atomic():
        for venda in vendas.select_related('produto'):
            produto = Produto.objects.select_for_update().get(id=venda.produto_id)
            produto.estoque_atual += venda.quantidade_vendida
            produto.save(update_fields=['estoque_atual'])
            _registrar_movimentacao_estoque(
                produto,
                'devolucao',
                venda.quantidade_vendida,
                request,
                observacao=f'Retorno por exclusÃ£o da transaÃ§Ã£o {transacao_id}',
            )
            total_itens += venda.quantidade_vendida

        num_produtos = vendas.count()
        vendas.delete()

    messages.success(request, f'Venda completa deletada! {num_produtos} produto(s) e {total_itens} unidade(s) restauradas ao estoque.')
    return HttpResponseRedirect(reverse('vendas:gestao_vendas'))


# ========================= RELATÃ“RIOS DE VENDAS/CLIENTES =========================

@login_required
@admin_requerido
def relatorios_dashboard(request):
    """Dashboard principal de relatÃ³rios"""
    from django.db.models.functions import TruncDate, TruncMonth

    hoje = timezone.now().date()
    periodo = request.GET.get('periodo', 'mes')
    if periodo == 'dia':
        data_inicio = hoje
        data_fim = hoje
    elif periodo == 'semana':
        data_inicio = hoje - timedelta(days=7)
        data_fim = hoje
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
    elif periodo == 'ano':
        data_inicio = hoje.replace(month=1, day=1)
        data_fim = hoje
    else:
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        if data_inicio and data_fim:
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
        else:
            data_inicio = hoje.replace(day=1)
            data_fim = hoje
    vendas_periodo = Venda.objects.filter(
        data_venda__range=[data_inicio, data_fim]
    )
    total_vendas = vendas_periodo.count()
    receita_total = sum(v.valor_total for v in vendas_periodo)
    lucro_total = sum(v.lucro for v in vendas_periodo)
    ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
    produtos_mais_vendidos = vendas_periodo.values(
        'produto__nome'
    ).annotate(
        quantidade=Sum('quantidade_vendida'),
        receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario'))
    ).order_by('-quantidade')[:10]
    produtos_menos_vendidos = vendas_periodo.values(
        'produto__nome'
    ).annotate(
        quantidade=Sum('quantidade_vendida'),
        receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario'))
    ).order_by('quantidade')[:10]
    if periodo == 'dia':
        evolucao = vendas_periodo.values('data_venda').annotate(
            vendas=Count('id'),
            receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario'))
        ).order_by('data_venda')
    elif periodo in ['semana', 'mes']:
        evolucao = vendas_periodo.annotate(
            data=TruncDate('data_venda')
        ).values('data').annotate(
            vendas=Count('id'),
            receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario'))
        ).order_by('data')
    else:
        evolucao = vendas_periodo.annotate(
            data=TruncMonth('data_venda')
        ).values('data').annotate(
            vendas=Count('id'),
            receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario'))
        ).order_by('data')
    evolucao_labels = [str(e['data'] if 'data' in e else e['data_venda']) for e in evolucao]
    evolucao_vendas = [e['vendas'] for e in evolucao]
    evolucao_receita = [float(e['receita']) for e in evolucao]
    vendas_por_categoria = vendas_periodo.values(
        'produto__categoria__nome'
    ).annotate(
        receita=Sum(F('quantidade_vendida') * F('preco_venda_unitario')),
        custo=Sum(F('quantidade_vendida') * F('produto__preco_custo_unitario')),
        quantidade=Sum('quantidade_vendida')
    )
    categorias_lucro = []
    for cat in vendas_por_categoria:
        if cat['produto__categoria__nome']:
            lucro = float(cat['receita']) - float(cat['custo'])
            margem = (lucro / float(cat['receita']) * 100) if cat['receita'] else 0
            categorias_lucro.append({
                'categoria': cat['produto__categoria__nome'],
                'receita': float(cat['receita']),
                'lucro': lucro,
                'margem_percentual': round(margem, 2),
                'quantidade': cat['quantidade']
            })
    dias_periodo = (data_fim - data_inicio).days + 1
    data_inicio_anterior = data_inicio - timedelta(days=dias_periodo)
    data_fim_anterior = data_inicio - timedelta(days=1)
    vendas_anterior = Venda.objects.filter(
        data_venda__range=[data_inicio_anterior, data_fim_anterior]
    )
    total_vendas_anterior = vendas_anterior.count()
    receita_anterior = sum(v.valor_total for v in vendas_anterior)
    lucro_anterior = sum(v.lucro for v in vendas_anterior)
    crescimento_vendas = ((total_vendas - total_vendas_anterior) / total_vendas_anterior * 100) if total_vendas_anterior else 0
    crescimento_receita = ((receita_total - receita_anterior) / receita_anterior * 100) if receita_anterior else 0
    crescimento_lucro = ((lucro_total - lucro_anterior) / lucro_anterior * 100) if lucro_anterior else 0
    context = {
        'periodo': periodo,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'total_vendas': total_vendas,
        'receita_total': receita_total,
        'lucro_total': lucro_total,
        'ticket_medio': ticket_medio,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'produtos_menos_vendidos': produtos_menos_vendidos,
        'evolucao_labels': json.dumps(evolucao_labels),
        'evolucao_vendas': json.dumps(evolucao_vendas),
        'evolucao_receita': json.dumps(evolucao_receita),
        'categorias_lucro': categorias_lucro,
        'crescimento_vendas': crescimento_vendas,
        'crescimento_receita': crescimento_receita,
        'crescimento_lucro': crescimento_lucro,
        'total_vendas_anterior': total_vendas_anterior,
        'receita_anterior': receita_anterior,
        'lucro_anterior': lucro_anterior,
    }
    return render(request, 'vendas/relatorios/dashboard.html', context)


@login_required
@vendedor_ou_admin
def relatorio_clientes(request):
    """RelatÃ³rio de clientes com ranking de compras"""
    from django.db.models import Max
    clientes_ranking = Cliente.objects.annotate(
        total_compras=Count('venda'),
        valor_total_compras=Sum(F('venda__quantidade_vendida') * F('venda__preco_venda_unitario'))
    ).filter(
        total_compras__gt=0
    ).order_by('-valor_total_compras')[:50]
    data_limite_inativo = timezone.now().date() - timedelta(days=90)
    clientes_inativos = Cliente.objects.annotate(
        ultima_compra=Max('venda__data_venda')
    ).filter(
        Q(ultima_compra__lt=data_limite_inativo) | Q(ultima_compra__isnull=True),
        ativo=True
    )
    clientes_devedores = []
    for cliente in Cliente.objects.filter(ativo=True):
        if cliente.saldo_devedor > 0:
            clientes_devedores.append({
                'cliente': cliente,
                'saldo': cliente.saldo_devedor
            })
    clientes_devedores.sort(key=lambda x: x['saldo'], reverse=True)
    context = {
        'clientes_ranking': clientes_ranking,
        'clientes_inativos': clientes_inativos,
        'clientes_devedores': clientes_devedores[:20],
    }
    return render(request, 'vendas/relatorios/clientes.html', context)


@login_required
@admin_requerido
def exportar_vendas_pdf(request):
    """Exporta relatÃ³rio de vendas em PDF"""
    vendas, data_inicio, data_fim = _build_vendas_export_queryset(request)
    return PDFExporter.exportar_vendas(vendas, data_inicio, data_fim)


@login_required
@admin_requerido
def exportar_vendas_excel(request):
    """Exporta relatÃ³rio de vendas em Excel"""
    vendas, data_inicio, data_fim = _build_vendas_export_queryset(request)
    return ExcelExporter.exportar_vendas(vendas, data_inicio, data_fim)


@login_required
@admin_requerido
def exportar_clientes_excel(request):
    """Exporta ranking de clientes em Excel"""
    clientes_ranking = Cliente.objects.annotate(
        total_compras=Count('venda'),
        valor_total_compras=Sum(F('venda__quantidade_vendida') * F('venda__preco_venda_unitario'))
    ).filter(
        total_compras__gt=0
    ).order_by('-valor_total_compras')[:100]
    return ExcelExporter.exportar_clientes(clientes_ranking)

