from django.contrib import admin
from .models import Cliente, Venda, Pagamento


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'cpf', 'saldo_devedor', 'total_compras', 'data_cadastro', 'ativo']
    list_filter = ['ativo', 'data_cadastro']
    search_fields = ['nome', 'telefone', 'cpf', 'email']
    date_hierarchy = 'data_cadastro'

    def saldo_devedor(self, obj):
        return f'R$ {obj.saldo_devedor:.2f}'
    saldo_devedor.short_description = 'Saldo Devedor'


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['produto', 'cliente', 'quantidade_vendida', 'preco_venda_unitario', 'valor_total', 'status_pagamento', 'data_venda']
    list_filter = ['status_pagamento', 'data_venda']
    search_fields = ['produto__nome', 'cliente__nome']
    date_hierarchy = 'data_venda'

    def valor_total(self, obj):
        return f'R$ {obj.valor_total:.2f}'
    valor_total.short_description = 'Valor Total'


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'venda', 'valor_pago', 'forma_pagamento', 'data_pagamento', 'criado_em']
    list_filter = ['forma_pagamento', 'data_pagamento']
    search_fields = ['cliente__nome', 'observacoes']
    date_hierarchy = 'data_pagamento'

    def valor_pago(self, obj):
        return f'R$ {obj.valor_pago:.2f}'
    valor_pago.short_description = 'Valor Pago'
