from django.contrib import admin
from .models import (
    ContaPagar,
    ContaReceber,
    ItemContaReceber,
    MovimentacaoCaixa,
    RecebimentoConta,
)


@admin.register(ContaPagar)
class ContaPagarAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'categoria', 'fornecedor', 'valor', 'data_vencimento', 'status']
    list_filter = ['categoria', 'status', 'data_vencimento']
    search_fields = ['descricao', 'fornecedor__nome']
    date_hierarchy = 'data_vencimento'


class ItemContaReceberInline(admin.TabularInline):
    model = ItemContaReceber
    extra = 0
    readonly_fields = ['subtotal']


class RecebimentoContaInline(admin.TabularInline):
    model = RecebimentoConta
    extra = 0
    readonly_fields = ['valor', 'forma_pagamento', 'data_recebimento', 'criado_em', 'criado_por']
    can_delete = False


@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'cliente', 'valor', 'total_recebido_admin', 'saldo_aberto_admin', 'data_vencimento', 'status', 'origem']
    list_filter = ['status', 'origem', 'data_vencimento']
    search_fields = ['descricao', 'cliente__nome', 'transacao_id']
    date_hierarchy = 'data_vencimento'
    inlines = [ItemContaReceberInline, RecebimentoContaInline]

    def total_recebido_admin(self, obj):
        return f'R$ {obj.total_recebido:.2f}'
    total_recebido_admin.short_description = 'Total Recebido'

    def saldo_aberto_admin(self, obj):
        return f'R$ {obj.saldo_aberto:.2f}'
    saldo_aberto_admin.short_description = 'Saldo Aberto'


@admin.register(RecebimentoConta)
class RecebimentoContaAdmin(admin.ModelAdmin):
    list_display = ['conta', 'valor', 'forma_pagamento', 'data_recebimento', 'criado_por', 'criado_em']
    list_filter = ['forma_pagamento', 'data_recebimento']
    search_fields = ['conta__descricao', 'conta__cliente__nome', 'observacoes']
    date_hierarchy = 'data_recebimento'


@admin.register(MovimentacaoCaixa)
class MovimentacaoCaixaAdmin(admin.ModelAdmin):
    list_display = ['data_movimentacao', 'tipo', 'categoria', 'descricao', 'valor', 'origem', 'criado_por']
    list_filter = ['tipo', 'categoria', 'data_movimentacao']
    search_fields = ['descricao', 'origem']
    date_hierarchy = 'data_movimentacao'