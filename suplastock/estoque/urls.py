from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    # Gestão de Produtos
    path('produtos/', views.gestao_produtos, name='gestao_produtos'),
    path('produtos/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/editar/<int:produto_id>/', views.editar_produto, name='editar_produto'),
    path('produtos/deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    
    # API
    path('api/produtos/todos/', views.api_produtos_todos, name='api_produtos_todos'),
    path('api/produtos/<int:produto_id>/detalhes/', views.api_produto_detalhes, name='api_produto_detalhes'),
    path('api/produtos/sku-preview/', views.api_sku_preview, name='api_sku_preview'),

    # Relatório de Estoque
    path('relatorios/estoque/', views.relatorio_estoque, name='relatorio_estoque'),

    # Exportação
    path('export/estoque/pdf/', views.exportar_estoque_pdf, name='exportar_estoque_pdf'),
    path('export/estoque/excel/', views.exportar_estoque_excel, name='exportar_estoque_excel'),
]
