from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, time
from decimal import Decimal, InvalidOperation

from django.db.utils import OperationalError, ProgrammingError
from django.db.models import (
    Avg,
    Case,
    Count,
    DecimalField,
    ExpressionWrapper,
    F,
    Max,
    Min,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, TruncMonth, TruncWeek
from django.utils import timezone

from estoque.models import Produto
from vendas.models import Pagamento, Venda
from .models import ContaPagar, ContaReceber, MovimentacaoCaixa, RecebimentoConta


MONEY_FIELD = DecimalField(max_digits=14, decimal_places=2)


TIPOS_RELATORIO = [
    ('geral', 'Geral'),
    ('vendas', 'Vendas'),
    ('clientes', 'Clientes'),
    ('lucro', 'Lucro'),
]


TIPOS_MOVIMENTACAO = [
    ('todos', 'Todos'),
    ('entrada', 'Entradas'),
    ('saida', 'Saídas'),
]


GRANULARIDADE_LABELS = {
    'dia': 'Diária',
    'semana': 'Semanal',
    'mes': 'Mensal',
}


def _money_zero():
    return Value(Decimal('0.00'), output_field=MONEY_FIELD)


def _safe_decimal(value):
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0')


def _venda_total_expression():
    return ExpressionWrapper(
        F('quantidade_vendida') * F('preco_venda_unitario'),
        output_field=MONEY_FIELD,
    )


def _venda_lucro_expression():
    return ExpressionWrapper(
        F('quantidade_vendida') * (F('preco_venda_unitario') - F('produto__preco_custo_unitario')),
        output_field=MONEY_FIELD,
    )


def _parse_date_value(raw_value):
    if not raw_value:
        return None
    if isinstance(raw_value, date):
        return raw_value
    try:
        return datetime.strptime(str(raw_value), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _normalizar_datetime_ordenacao(value):
    if not isinstance(value, datetime):
        return datetime.min
    if timezone.is_aware(value):
        return timezone.localtime(value).replace(tzinfo=None)
    return value


def parse_periodo_datas(data_inicio_raw=None, data_fim_raw=None, *, default_days=None):
    hoje = timezone.localdate()
    if default_days is None:
        data_inicio_default = hoje.replace(day=1)
    else:
        data_inicio_default = hoje - timedelta(days=max(0, int(default_days)))

    data_inicio = _parse_date_value(data_inicio_raw) or data_inicio_default
    data_fim = _parse_date_value(data_fim_raw) or hoje

    if data_inicio > data_fim:
        data_inicio, data_fim = data_fim, data_inicio
    return data_inicio, data_fim


def _detectar_granularidade(data_inicio, data_fim):
    total_dias = (data_fim - data_inicio).days + 1
    if total_dias <= 14:
        return 'dia'
    if total_dias <= 120:
        return 'semana'
    return 'mes'


def _normalizar_para_data(value):
    if isinstance(value, datetime):
        return value.date()
    return value


def _inicio_periodo(data_ref, granularidade):
    if granularidade == 'mes':
        return data_ref.replace(day=1)
    if granularidade == 'semana':
        return data_ref - timedelta(days=data_ref.weekday())
    return data_ref


def _iterar_periodos(data_inicio, data_fim, granularidade):
    cursor = _inicio_periodo(data_inicio, granularidade)
    limite = _inicio_periodo(data_fim, granularidade)

    while cursor <= limite:
        yield cursor
        if granularidade == 'dia':
            cursor += timedelta(days=1)
        elif granularidade == 'semana':
            cursor += timedelta(days=7)
        else:
            if cursor.month == 12:
                cursor = cursor.replace(year=cursor.year + 1, month=1, day=1)
            else:
                cursor = cursor.replace(month=cursor.month + 1, day=1)


def _label_periodo(periodo_inicio, granularidade):
    if granularidade == 'dia':
        return periodo_inicio.strftime('%d/%m')
    if granularidade == 'semana':
        ano_iso, semana_iso, _ = periodo_inicio.isocalendar()
        return f'Sem {semana_iso:02d}/{str(ano_iso)[-2:]}'
    return periodo_inicio.strftime('%m/%Y')


def _contas_receber_com_saldo_queryset():
    recebimentos_subquery = (
        RecebimentoConta.objects
        .filter(conta_id=OuterRef('pk'))
        .values('conta_id')
        .annotate(total=Sum('valor'))
        .values('total')[:1]
    )

    return (
        ContaReceber.objects
        .exclude(status='cancelado')
        .select_related('cliente', 'venda')
        .annotate(
            total_recebido_calc=Coalesce(
                Subquery(recebimentos_subquery, output_field=MONEY_FIELD),
                _money_zero(),
                output_field=MONEY_FIELD,
            )
        )
        .annotate(
            saldo_aberto_calc=ExpressionWrapper(
                F('valor') - F('total_recebido_calc'),
                output_field=MONEY_FIELD,
            )
        )
    )


def _classificar_risco(dias_em_atraso):
    if dias_em_atraso <= 7:
        return 'leve', 'Leve'
    if dias_em_atraso <= 30:
        return 'medio', 'Médio'
    return 'grave', 'Grave'


def build_relatorios_context(*, data_inicio, data_fim, tipo_relatorio='geral'):
    hoje = timezone.localdate()
    valor_venda_expr = _venda_total_expression()
    lucro_venda_expr = _venda_lucro_expression()

    vendas_periodo_qs = (
        Venda.objects
        .filter(data_venda__range=(data_inicio, data_fim))
        .select_related('cliente', 'produto', 'produto__categoria')
    )
    pagamentos_periodo_qs = Pagamento.objects.filter(data_pagamento__range=(data_inicio, data_fim))

    cards = vendas_periodo_qs.aggregate(
        total_vendas=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD),
        lucro_estimado=Coalesce(Sum(lucro_venda_expr), _money_zero(), output_field=MONEY_FIELD),
        quantidade_vendas=Count('id'),
    )
    total_recebido = pagamentos_periodo_qs.aggregate(
        total=Coalesce(Sum('valor_pago'), _money_zero(), output_field=MONEY_FIELD)
    )['total']

    quantidade_vendas = int(cards['quantidade_vendas'] or 0)
    total_vendas = _safe_decimal(cards['total_vendas'])
    ticket_medio = (total_vendas / quantidade_vendas) if quantidade_vendas else Decimal('0')
    lucro_estimado = _safe_decimal(cards['lucro_estimado'])

    granularidade = _detectar_granularidade(data_inicio, data_fim)
    if granularidade == 'semana':
        periodo_expr = TruncWeek('data_venda')
    elif granularidade == 'mes':
        periodo_expr = TruncMonth('data_venda')
    else:
        periodo_expr = F('data_venda')

    serie_qs = (
        vendas_periodo_qs
        .annotate(periodo=periodo_expr)
        .values('periodo')
        .annotate(
            receita=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD),
            lucro=Coalesce(Sum(lucro_venda_expr), _money_zero(), output_field=MONEY_FIELD),
            quantidade=Count('id'),
        )
        .order_by('periodo')
    )

    vendas_por_periodo = []
    lucro_por_periodo = []
    chart_labels = []
    chart_vendas = []
    chart_lucros = []
    chart_margens = []
    chart_quantidades = []

    for row in serie_qs:
        periodo = _normalizar_para_data(row['periodo'])
        label = _label_periodo(periodo, granularidade)
        receita = _safe_decimal(row['receita'])
        lucro = _safe_decimal(row['lucro'])
        quantidade = int(row['quantidade'] or 0)
        margem = (lucro / receita * Decimal('100')) if receita > 0 else Decimal('0')

        vendas_por_periodo.append({
            'label': label,
            'receita': receita,
            'quantidade': quantidade,
        })
        lucro_por_periodo.append({
            'label': label,
            'lucro': lucro,
        })

        chart_labels.append(label)
        chart_vendas.append(float(receita))
        chart_lucros.append(float(lucro))
        chart_margens.append(float(margem))
        chart_quantidades.append(quantidade)

    chart_data = {
        'granularidade': granularidade,
        'granularidade_label': GRANULARIDADE_LABELS.get(granularidade, 'Automática'),
        'labels': chart_labels,
        'vendas': chart_vendas,
        'lucros': chart_lucros,
        'margens': chart_margens,
        'quantidades': chart_quantidades,
    }

    produtos_mais_vendidos = list(
        vendas_periodo_qs
        .values('produto__nome')
        .annotate(
            quantidade=Coalesce(Sum('quantidade_vendida'), 0),
            receita=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD),
        )
        .order_by('-quantidade', '-receita')[:10]
    )

    clientes_mais_compram = list(
        vendas_periodo_qs
        .filter(cliente__isnull=False)
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            quantidade_vendas=Count('id'),
            total_comprado=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD),
            ticket_medio=Coalesce(Avg(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD),
        )
        .order_by('-total_comprado', '-quantidade_vendas')[:10]
    )

    inadimplentes_qs = (
        _contas_receber_com_saldo_queryset()
        .filter(
            saldo_aberto_calc__gt=0,
            data_vencimento__lt=hoje,
        )
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            valor_em_aberto=Coalesce(Sum('saldo_aberto_calc'), _money_zero(), output_field=MONEY_FIELD),
            contas_em_atraso=Count('id'),
            vencimento_mais_antigo=Min('data_vencimento'),
        )
        .order_by('-valor_em_aberto')[:10]
    )
    clientes_inadimplentes = []
    for item in inadimplentes_qs:
        vencimento_antigo = item['vencimento_mais_antigo']
        dias_atraso = (hoje - vencimento_antigo).days if vencimento_antigo else 0
        clientes_inadimplentes.append({
            'cliente_id': item['cliente_id'],
            'cliente_nome': item['cliente__nome'],
            'cliente_codigo': item['cliente__codigo'] or '',
            'valor_em_aberto': _safe_decimal(item['valor_em_aberto']),
            'contas_em_atraso': int(item['contas_em_atraso'] or 0),
            'dias_atraso': dias_atraso,
        })

    compras_por_cliente = (
        vendas_periodo_qs
        .filter(cliente__isnull=False)
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            total_comprado=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD)
        )
    )
    pagamentos_por_cliente = (
        pagamentos_periodo_qs
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            total_pago=Coalesce(Sum('valor_pago'), _money_zero(), output_field=MONEY_FIELD)
        )
    )
    saldos_por_cliente = (
        _contas_receber_com_saldo_queryset()
        .filter(saldo_aberto_calc__gt=0)
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            saldo_aberto=Coalesce(
                Sum(
                    Case(
                        When(saldo_aberto_calc__gt=0, then=F('saldo_aberto_calc')),
                        default=_money_zero(),
                        output_field=MONEY_FIELD,
                    )
                ),
                _money_zero(),
                output_field=MONEY_FIELD,
            )
        )
    )

    tabela_clientes_map = {}
    for row in compras_por_cliente:
        cliente_id = row['cliente_id']
        if not cliente_id:
            continue
        tabela_clientes_map[cliente_id] = {
            'cliente_id': cliente_id,
            'cliente_nome': row['cliente__nome'] or '-',
            'cliente_codigo': row['cliente__codigo'] or '',
            'total_comprado': _safe_decimal(row['total_comprado']),
            'total_pago': Decimal('0'),
            'saldo_em_aberto': Decimal('0'),
        }

    for row in pagamentos_por_cliente:
        cliente_id = row['cliente_id']
        if not cliente_id:
            continue
        item = tabela_clientes_map.get(cliente_id)
        if not item:
            item = {
                'cliente_id': cliente_id,
                'cliente_nome': row['cliente__nome'] or '-',
                'cliente_codigo': row['cliente__codigo'] or '',
                'total_comprado': Decimal('0'),
                'total_pago': Decimal('0'),
                'saldo_em_aberto': Decimal('0'),
            }
            tabela_clientes_map[cliente_id] = item
        item['total_pago'] = _safe_decimal(row['total_pago'])

    for row in saldos_por_cliente:
        cliente_id = row['cliente_id']
        if not cliente_id:
            continue
        item = tabela_clientes_map.get(cliente_id)
        if not item:
            item = {
                'cliente_id': cliente_id,
                'cliente_nome': row['cliente__nome'] or '-',
                'cliente_codigo': row['cliente__codigo'] or '',
                'total_comprado': Decimal('0'),
                'total_pago': Decimal('0'),
                'saldo_em_aberto': Decimal('0'),
            }
            tabela_clientes_map[cliente_id] = item
        item['saldo_em_aberto'] = _safe_decimal(row['saldo_aberto'])

    tabela_clientes = sorted(
        tabela_clientes_map.values(),
        key=lambda item: (item['total_comprado'], item['saldo_em_aberto']),
        reverse=True,
    )[:35]

    return {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_relatorio': tipo_relatorio if tipo_relatorio in dict(TIPOS_RELATORIO) else 'geral',
        'tipos_relatorio': TIPOS_RELATORIO,
        'total_vendas': total_vendas,
        'total_recebido': _safe_decimal(total_recebido),
        'lucro_estimado': lucro_estimado,
        'quantidade_vendas': quantidade_vendas,
        'ticket_medio': ticket_medio,
        'vendas_por_periodo': vendas_por_periodo,
        'lucro_por_periodo': lucro_por_periodo,
        'chart_data': chart_data,
        'chart_granularidade': granularidade,
        'chart_granularidade_label': GRANULARIDADE_LABELS.get(granularidade, 'Automática'),
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'clientes_mais_compram': clientes_mais_compram,
        'clientes_inadimplentes': clientes_inadimplentes,
        'tabela_clientes': tabela_clientes,
    }


def build_inadimplencia_context(*, cliente_busca=''):
    hoje = timezone.localdate()
    contas_atrasadas_qs = _contas_receber_com_saldo_queryset().filter(
        saldo_aberto_calc__gt=0,
        data_vencimento__lt=hoje,
    )
    if cliente_busca:
        contas_atrasadas_qs = contas_atrasadas_qs.filter(
            Q(cliente__nome__icontains=cliente_busca) | Q(cliente__codigo__icontains=cliente_busca)
        )

    consolidados = list(
        contas_atrasadas_qs
        .values('cliente_id', 'cliente__nome', 'cliente__codigo')
        .annotate(
            valor_em_atraso=Coalesce(Sum('saldo_aberto_calc'), _money_zero(), output_field=MONEY_FIELD),
            contas_em_atraso=Count('id'),
            vencimento_mais_antigo=Min('data_vencimento'),
        )
        .order_by('-valor_em_atraso', 'cliente__nome')
    )

    cliente_ids = [item['cliente_id'] for item in consolidados if item['cliente_id']]
    ultimas_compras_map = {
        item['cliente_id']: item['ultima_compra']
        for item in (
            Venda.objects
            .filter(cliente_id__in=cliente_ids)
            .values('cliente_id')
            .annotate(ultima_compra=Max('data_venda'))
        )
    }
    ultimos_pagamentos_map = {
        item['cliente_id']: item['ultimo_pagamento']
        for item in (
            Pagamento.objects
            .filter(cliente_id__in=cliente_ids)
            .values('cliente_id')
            .annotate(ultimo_pagamento=Max('data_pagamento'))
        )
    }

    clientes = []
    total_em_atraso = Decimal('0')
    total_dias = 0
    maior_divida = Decimal('0')
    for item in consolidados:
        cliente_id = item['cliente_id']
        valor_em_atraso = _safe_decimal(item['valor_em_atraso'])
        vencimento_antigo = item['vencimento_mais_antigo']
        dias_em_atraso = (hoje - vencimento_antigo).days if vencimento_antigo else 0
        risco_codigo, risco_label = _classificar_risco(dias_em_atraso)

        total_em_atraso += valor_em_atraso
        total_dias += dias_em_atraso
        if valor_em_atraso > maior_divida:
            maior_divida = valor_em_atraso

        clientes.append({
            'cliente_id': cliente_id,
            'cliente_nome': item['cliente__nome'] or '-',
            'cliente_codigo': item['cliente__codigo'] or '',
            'valor_em_atraso': valor_em_atraso,
            'contas_em_atraso': int(item['contas_em_atraso'] or 0),
            'dias_em_atraso': dias_em_atraso,
            'vencimento_mais_antigo': vencimento_antigo,
            'ultima_compra': ultimas_compras_map.get(cliente_id),
            'ultimo_pagamento': ultimos_pagamentos_map.get(cliente_id),
            'risco_codigo': risco_codigo,
            'risco_label': risco_label,
        })

    quantidade_clientes = len(clientes)
    media_dias = Decimal('0')
    if quantidade_clientes:
        media_dias = Decimal(str(round(total_dias / quantidade_clientes, 1)))

    ranking_por_divida = clientes[:5]
    ranking_por_atraso = sorted(
        clientes,
        key=lambda item: (item['dias_em_atraso'], item['valor_em_atraso']),
        reverse=True,
    )[:5]

    return {
        'cliente_busca': cliente_busca,
        'clientes_inadimplentes': clientes,
        'total_em_atraso': total_em_atraso,
        'quantidade_clientes_inadimplentes': quantidade_clientes,
        'media_dias_atraso': media_dias,
        'maior_divida_em_atraso': maior_divida,
        'ranking_maior_divida': ranking_por_divida,
        'ranking_maior_atraso': ranking_por_atraso,
        'hoje': hoje,
    }


def build_alertas_context():
    hoje = timezone.localdate()
    contas_abertas_qs = _contas_receber_com_saldo_queryset().filter(saldo_aberto_calc__gt=0)

    contas_vencendo_hoje_qs = (
        contas_abertas_qs
        .filter(data_vencimento=hoje)
        .order_by('-saldo_aberto_calc', 'cliente__nome')
    )
    contas_atrasadas_qs = (
        contas_abertas_qs
        .filter(data_vencimento__lt=hoje)
        .order_by('data_vencimento', '-saldo_aberto_calc')
    )

    contas_vencendo_hoje = []
    for conta in contas_vencendo_hoje_qs[:20]:
        contas_vencendo_hoje.append({
            'conta_id': conta.id,
            'cliente_id': conta.cliente_id,
            'cliente_nome': conta.cliente.nome if conta.cliente_id else '-',
            'descricao': conta.descricao,
            'valor': _safe_decimal(getattr(conta, 'saldo_aberto_calc', conta.valor)),
            'vencimento': conta.data_vencimento,
        })

    contas_atrasadas = []
    for conta in contas_atrasadas_qs[:20]:
        dias_atraso = (hoje - conta.data_vencimento).days
        contas_atrasadas.append({
            'conta_id': conta.id,
            'cliente_id': conta.cliente_id,
            'cliente_nome': conta.cliente.nome if conta.cliente_id else '-',
            'descricao': conta.descricao,
            'valor': _safe_decimal(getattr(conta, 'saldo_aberto_calc', conta.valor)),
            'dias_atraso': dias_atraso,
            'vencimento': conta.data_vencimento,
        })

    estoque_baixo = list(
        Produto.objects
        .filter(
            ativo=True,
            estoque_atual__gt=0,
            estoque_atual__lte=F('estoque_minimo'),
        )
        .select_related('categoria')
        .order_by('estoque_atual', 'nome')[:20]
    )
    produtos_sem_estoque = list(
        Produto.objects
        .filter(ativo=True, estoque_atual__lte=0)
        .select_related('categoria')
        .order_by('nome')[:20]
    )

    contas_pagar_vencendo_hoje = list(
        ContaPagar.objects
        .filter(status__in=['pendente', 'atrasado'], data_vencimento=hoje)
        .order_by('-valor', 'descricao')[:20]
    )
    contas_pagar_atrasadas = []
    for conta in (
        ContaPagar.objects
        .filter(status__in=['pendente', 'atrasado'], data_vencimento__lt=hoje)
        .order_by('data_vencimento', '-valor')[:20]
    ):
        contas_pagar_atrasadas.append({
            'id': conta.id,
            'descricao': conta.descricao,
            'categoria': conta.get_categoria_display(),
            'valor': _safe_decimal(conta.valor),
            'data_vencimento': conta.data_vencimento,
            'dias_atraso': (hoje - conta.data_vencimento).days,
        })

    alertas_criticos = (
        len(contas_atrasadas)
        + len(produtos_sem_estoque)
        + len(contas_pagar_atrasadas)
    )
    alertas_hoje = len(contas_vencendo_hoje) + len(contas_pagar_vencendo_hoje)
    total_alertas = (
        len(contas_vencendo_hoje)
        + len(contas_atrasadas)
        + len(estoque_baixo)
        + len(produtos_sem_estoque)
        + len(contas_pagar_vencendo_hoje)
        + len(contas_pagar_atrasadas)
    )

    return {
        'hoje': hoje,
        'contas_vencendo_hoje': contas_vencendo_hoje,
        'contas_atrasadas': contas_atrasadas,
        'estoque_baixo': estoque_baixo,
        'produtos_sem_estoque': produtos_sem_estoque,
        'contas_pagar_vencendo_hoje': contas_pagar_vencendo_hoje,
        'contas_pagar_atrasadas': contas_pagar_atrasadas,
        'total_alertas_estoque': len(estoque_baixo) + len(produtos_sem_estoque),
        'total_alertas': total_alertas,
        'alertas_criticos': alertas_criticos,
        'alertas_hoje': alertas_hoje,
    }


def _categoria_saida_conta_pagar(conta):
    if conta.categoria == 'fornecedor':
        return 'compra_fornecedor', 'Compra de fornecedor'
    if conta.categoria in {
        'aluguel', 'energia', 'agua', 'internet', 'telefone',
        'salario', 'impostos', 'marketing', 'manutencao',
    }:
        return 'despesa_operacional', 'Despesa operacional'
    if conta.categoria == 'retirada':
        return 'retirada', 'Retirada'
    return 'saida_manual', 'Saída manual'


def _movimentacao_caixa_tabela_indisponivel(exc):
    mensagem = str(exc).lower()
    return (
        'gestao_movimentacaocaixa' in mensagem
        and ('no such table' in mensagem or 'does not exist' in mensagem)
    )


def calcular_saldo_caixa_ate(data_limite):
    if not data_limite:
        return Decimal('0')

    valor_venda_expr = _venda_total_expression()
    entradas_vendas_vista = (
        Venda.objects
        .filter(
            data_venda__lte=data_limite,
            status_pagamento='Pago',
            pagamento__isnull=True,
        )
        .aggregate(total=Coalesce(Sum(valor_venda_expr), _money_zero(), output_field=MONEY_FIELD))
    )['total']

    entradas_pagamentos = (
        Pagamento.objects
        .filter(data_pagamento__lte=data_limite)
        .aggregate(total=Coalesce(Sum('valor_pago'), _money_zero(), output_field=MONEY_FIELD))
    )['total']

    saidas_contas_pagar = (
        ContaPagar.objects
        .filter(status='pago', data_pagamento__lte=data_limite)
        .aggregate(total=Coalesce(Sum('valor'), _money_zero(), output_field=MONEY_FIELD))
    )['total']

    entradas_manuais = Decimal('0')
    saidas_manuais = Decimal('0')
    try:
        entradas_manuais = (
            MovimentacaoCaixa.objects
            .filter(tipo='entrada', data_movimentacao__lte=data_limite)
            .aggregate(total=Coalesce(Sum('valor'), _money_zero(), output_field=MONEY_FIELD))
        )['total']
        saidas_manuais = (
            MovimentacaoCaixa.objects
            .filter(tipo='saida', data_movimentacao__lte=data_limite)
            .aggregate(total=Coalesce(Sum('valor'), _money_zero(), output_field=MONEY_FIELD))
        )['total']
    except (OperationalError, ProgrammingError) as exc:
        if not _movimentacao_caixa_tabela_indisponivel(exc):
            raise
        manuais_qs = []

    return (
        _safe_decimal(entradas_vendas_vista)
        + _safe_decimal(entradas_pagamentos)
        + _safe_decimal(entradas_manuais)
        - _safe_decimal(saidas_contas_pagar)
        - _safe_decimal(saidas_manuais)
    )


def _build_movimentacoes_periodo(data_inicio, data_fim):
    movimentos = []
    sequencia = 0
    valor_venda_expr = _venda_total_expression()

    vendas_vista_qs = (
        Venda.objects
        .filter(
            data_venda__range=(data_inicio, data_fim),
            status_pagamento='Pago',
            pagamento__isnull=True,
        )
        .select_related('produto', 'cliente')
        .annotate(valor_total_calc=valor_venda_expr)
        .order_by('data_venda', 'id')
    )
    for venda in vendas_vista_qs:
        descricao_cliente = f' ({venda.cliente.nome})' if venda.cliente_id else ''
        movimentos.append({
            'data': venda.data_venda,
            'tipo': 'entrada',
            'tipo_display': 'Entrada',
            'categoria': 'venda_a_vista',
            'categoria_display': 'Venda à vista',
            'descricao': f'Venda à vista: {venda.produto.nome}{descricao_cliente}',
            'valor': _safe_decimal(getattr(venda, 'valor_total_calc', venda.valor_total)),
            'origem': 'Gestão de Vendas',
            'usuario': '-',
            'criado_em': _normalizar_datetime_ordenacao(
                datetime.combine(venda.data_venda, time.min)
            ),
            'sequencia': sequencia,
        })
        sequencia += 1

    pagamentos_qs = (
        Pagamento.objects
        .filter(data_pagamento__range=(data_inicio, data_fim))
        .select_related('cliente', 'venda')
        .order_by('data_pagamento', 'id')
    )
    for pagamento in pagamentos_qs:
        observacao = (pagamento.observacoes or '').strip()
        observacao_lower = observacao.lower()
        eh_conta_receber = 'conta #' in observacao_lower or 'conta ' in observacao_lower
        origem = 'Contas a Receber' if eh_conta_receber else 'Cobrança'
        descricao_base = observacao or (
            f'Recebimento de {pagamento.cliente.nome}'
            if pagamento.cliente_id else 'Recebimento'
        )

        movimentos.append({
            'data': pagamento.data_pagamento,
            'tipo': 'entrada',
            'tipo_display': 'Entrada',
            'categoria': 'pagamento_fiado',
            'categoria_display': 'Pagamento de fiado',
            'descricao': descricao_base,
            'valor': _safe_decimal(pagamento.valor_pago),
            'origem': origem,
            'usuario': '-',
            'criado_em': _normalizar_datetime_ordenacao(
                datetime.combine(pagamento.data_pagamento, time.min)
            ),
            'sequencia': sequencia,
        })
        sequencia += 1

    contas_pagar_qs = (
        ContaPagar.objects
        .filter(status='pago', data_pagamento__range=(data_inicio, data_fim))
        .select_related('fornecedor')
        .order_by('data_pagamento', 'id')
    )
    for conta in contas_pagar_qs:
        categoria_codigo, categoria_display = _categoria_saida_conta_pagar(conta)
        fornecedor = f' - {conta.fornecedor.nome}' if conta.fornecedor_id else ''
        movimentos.append({
            'data': conta.data_pagamento,
            'tipo': 'saida',
            'tipo_display': 'Saída',
            'categoria': categoria_codigo,
            'categoria_display': categoria_display,
            'descricao': f'{conta.descricao}{fornecedor}',
            'valor': _safe_decimal(conta.valor),
            'origem': 'Contas a Pagar',
            'usuario': '-',
            'criado_em': _normalizar_datetime_ordenacao(
                datetime.combine(conta.data_pagamento, time.min)
            ),
            'sequencia': sequencia,
        })
        sequencia += 1

    manuais_qs = []
    try:
        manuais_qs = (
            MovimentacaoCaixa.objects
            .filter(data_movimentacao__range=(data_inicio, data_fim))
            .select_related('criado_por')
            .order_by('data_movimentacao', 'criado_em', 'id')
        )
        manuais_qs = list(manuais_qs)
    except (OperationalError, ProgrammingError) as exc:
        if not _movimentacao_caixa_tabela_indisponivel(exc):
            raise
        manuais_qs = []
    for movimento in manuais_qs:
        usuario_nome = '-'
        if movimento.criado_por:
            nome_completo = (
                movimento.criado_por.get_full_name().strip()
                if hasattr(movimento.criado_por, 'get_full_name')
                else ''
            )
            usuario_nome = nome_completo or movimento.criado_por.username

        movimentos.append({
            'data': movimento.data_movimentacao,
            'tipo': movimento.tipo,
            'tipo_display': movimento.get_tipo_display(),
            'categoria': movimento.categoria,
            'categoria_display': movimento.get_categoria_display(),
            'descricao': movimento.descricao,
            'valor': _safe_decimal(movimento.valor),
            'origem': movimento.origem,
            'usuario': usuario_nome,
            'criado_em': _normalizar_datetime_ordenacao(movimento.criado_em),
            'sequencia': sequencia,
        })
        sequencia += 1

    movimentos.sort(
        key=lambda item: (
            item['data'],
            _normalizar_datetime_ordenacao(item.get('criado_em')),
            item['sequencia'],
        )
    )
    return movimentos


def _series_fluxo(movimentos, saldo_inicial_periodo, data_inicio, data_fim):
    granularidade = _detectar_granularidade(data_inicio, data_fim)

    buckets = defaultdict(lambda: {'entrada': Decimal('0'), 'saida': Decimal('0')})
    for item in movimentos:
        chave = _inicio_periodo(item['data'], granularidade)
        buckets[chave][item['tipo']] += _safe_decimal(item['valor'])

    labels = []
    entradas = []
    saidas = []
    saldos = []
    saldo_corrente = _safe_decimal(saldo_inicial_periodo)

    for chave in _iterar_periodos(data_inicio, data_fim, granularidade):
        total_entrada = _safe_decimal(buckets[chave]['entrada'])
        total_saida = _safe_decimal(buckets[chave]['saida'])
        saldo_corrente += total_entrada - total_saida

        labels.append(_label_periodo(chave, granularidade))
        entradas.append(float(total_entrada))
        saidas.append(float(total_saida))
        saldos.append(float(saldo_corrente))

    return {
        'granularidade': granularidade,
        'granularidade_label': GRANULARIDADE_LABELS.get(granularidade, 'Automática'),
        'movimento': {
            'labels': labels,
            'entradas': entradas,
            'saidas': saidas,
        },
        'saldo': {
            'labels': labels,
            'saldos': saldos,
        },
    }


def build_fluxo_caixa_context(*, data_inicio, data_fim, tipo_movimentacao='todos', ordenacao='desc'):
    hoje = timezone.localdate()
    tipo_normalizado = tipo_movimentacao if tipo_movimentacao in {'todos', 'entrada', 'saida'} else 'todos'
    ordenacao_normalizada = ordenacao if ordenacao in {'asc', 'desc'} else 'desc'

    saldo_ate_ontem_periodo = calcular_saldo_caixa_ate(data_inicio - timedelta(days=1))
    movimentos = _build_movimentacoes_periodo(data_inicio, data_fim)

    total_entradas_periodo = sum(
        (_safe_decimal(item['valor']) for item in movimentos if item['tipo'] == 'entrada'),
        Decimal('0'),
    )
    total_saidas_periodo = sum(
        (_safe_decimal(item['valor']) for item in movimentos if item['tipo'] == 'saida'),
        Decimal('0'),
    )
    saldo_periodo = total_entradas_periodo - total_saidas_periodo

    saldo_corrente = _safe_decimal(saldo_ate_ontem_periodo)
    for item in movimentos:
        if item['tipo'] == 'entrada':
            saldo_corrente += _safe_decimal(item['valor'])
        else:
            saldo_corrente -= _safe_decimal(item['valor'])
        item['saldo_acumulado'] = saldo_corrente

    movimentos_filtrados = movimentos
    if tipo_normalizado in {'entrada', 'saida'}:
        movimentos_filtrados = [item for item in movimentos if item['tipo'] == tipo_normalizado]

    if ordenacao_normalizada == 'desc':
        movimentos_filtrados = list(reversed(movimentos_filtrados))

    saldo_atual = calcular_saldo_caixa_ate(hoje)
    saldo_ate_ontem = calcular_saldo_caixa_ate(hoje - timedelta(days=1))
    saldo_dia = saldo_atual - saldo_ate_ontem

    primeiro_dia_mes = hoje.replace(day=1)
    saldo_antes_mes = calcular_saldo_caixa_ate(primeiro_dia_mes - timedelta(days=1))
    saldo_mes = saldo_atual - saldo_antes_mes

    chart_data = _series_fluxo(
        movimentos=movimentos,
        saldo_inicial_periodo=saldo_ate_ontem_periodo,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    return {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'tipo_movimentacao': tipo_normalizado,
        'ordenacao': ordenacao_normalizada,
        'tipos_movimentacao': TIPOS_MOVIMENTACAO,
        'movimentacoes_periodo': list(movimentos),
        'movimentacoes': movimentos_filtrados,
        'total_entradas_periodo': total_entradas_periodo,
        'total_saidas_periodo': total_saidas_periodo,
        'saldo_periodo': saldo_periodo,
        'saldo_inicio_periodo': _safe_decimal(saldo_ate_ontem_periodo),
        'saldo_final_periodo': _safe_decimal(saldo_ate_ontem_periodo) + saldo_periodo,
        'saldo_atual': saldo_atual,
        'saldo_dia': saldo_dia,
        'saldo_mes': saldo_mes,
        'chart_data': chart_data,
    }


def registrar_movimentacao_manual(
    *,
    tipo,
    categoria,
    descricao,
    valor_raw,
    data_movimentacao_raw,
    usuario=None,
):
    tipo_normalizado = (tipo or '').strip().lower()
    if tipo_normalizado not in {'entrada', 'saida'}:
        raise ValueError('Tipo de movimentação inválido.')

    try:
        valor = Decimal(str(valor_raw))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError('Valor inválido.')
    if valor <= 0:
        raise ValueError('Valor deve ser maior que zero.')

    data_movimentacao = _parse_date_value(data_movimentacao_raw)
    if not data_movimentacao:
        raise ValueError('Data da movimentação inválida.')

    descricao_normalizada = (descricao or '').strip()
    if not descricao_normalizada:
        raise ValueError('Descrição é obrigatória.')

    categoria_normalizada = (categoria or '').strip()
    categorias_entrada = {'venda_a_vista', 'pagamento_fiado', 'entrada_manual'}
    categorias_saida = {'despesa_operacional', 'compra_fornecedor', 'retirada', 'saida_manual'}

    if tipo_normalizado == 'entrada' and categoria_normalizada not in categorias_entrada:
        categoria_normalizada = 'entrada_manual'
    if tipo_normalizado == 'saida' and categoria_normalizada not in categorias_saida:
        categoria_normalizada = 'saida_manual'

    try:
        return MovimentacaoCaixa.objects.create(
            data_movimentacao=data_movimentacao,
            tipo=tipo_normalizado,
            categoria=categoria_normalizada,
            descricao=descricao_normalizada,
            valor=valor,
            origem='Lançamento Manual',
            criado_por=usuario if getattr(usuario, 'is_authenticated', False) else None,
        )
    except (OperationalError, ProgrammingError) as exc:
        if _movimentacao_caixa_tabela_indisponivel(exc):
            raise ValueError('Módulo de caixa ainda não migrado. Execute: python manage.py migrate')
        raise