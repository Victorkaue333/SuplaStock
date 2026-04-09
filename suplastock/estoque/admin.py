from django.contrib import admin
from .models import Categoria, Produto, Fornecedor, AlertaEstoque, MovimentacaoEstoque


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['sku', 'nome', 'categoria', 'fornecedor', 'estoque_atual', 'estoque_minimo', 'preco_custo_unitario', 'margem_lucro_percentual', 'data_validade', 'ativo']
    list_filter = ['categoria', 'ativo', 'data_compra']
    search_fields = ['nome', 'sku', 'lote']
    date_hierarchy = 'data_compra'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'sku', 'categoria', 'fornecedor', 'imagem', 'ativo')
        }),
        ('Estoque', {
            'fields': ('quantidade_comprada', 'estoque_atual', 'estoque_minimo', 'data_compra')
        }),
        ('Lote e Validade', {
            'fields': ('lote', 'data_fabricacao', 'data_validade')
        }),
        ('Preços', {
            'fields': ('preco_custo_unitario', 'preco_venda_sugerido', 'margem_lucro_percentual')
        }),
    )

    readonly_fields = ['margem_lucro_percentual', 'criado_em', 'atualizado_em']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cnpj', 'telefone', 'email', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'cnpj', 'email']


@admin.register(AlertaEstoque)
class AlertaEstoqueAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tipo_alerta', 'status', 'criado_em', 'visualizado_em']
    list_filter = ['tipo_alerta', 'status', 'criado_em']
    search_fields = ['produto__nome', 'mensagem']
    date_hierarchy = 'criado_em'

    actions = ['marcar_como_visualizado', 'marcar_como_resolvido']

    def marcar_como_visualizado(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='visualizado', visualizado_em=timezone.now())
        self.message_user(request, f'{queryset.count()} alertas marcados como visualizados.')
    marcar_como_visualizado.short_description = 'Marcar como visualizado'

    def marcar_como_resolvido(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='resolvido', resolvido_em=timezone.now(), resolvido_por=request.user)
        self.message_user(request, f'{queryset.count()} alertas marcados como resolvidos.')
    marcar_como_resolvido.short_description = 'Marcar como resolvido'


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ['data_movimentacao', 'produto', 'tipo_movimentacao', 'quantidade', 'usuario_responsavel']
    list_filter = ['tipo_movimentacao', 'data_movimentacao']
    search_fields = ['produto__nome', 'produto__sku', 'observacao', 'usuario_responsavel__username']
    date_hierarchy = 'data_movimentacao'
