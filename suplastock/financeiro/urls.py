from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard Financeiro
    path('financeiro/', views.dashboard_financeiro, name='dashboard_financeiro'),
    path('financeiro/exportar/', views.exportar_dashboard_financeiro, name='exportar_dashboard_financeiro'),

    # Painéis de gestão (novo módulo)
    path('financeiro/relatorios/', views.relatorios_gerenciais, name='relatorios_gerenciais'),
    path('financeiro/inadimplencia/', views.inadimplencia, name='inadimplencia'),
    path('financeiro/alertas/', views.alertas_notificacoes, name='alertas_notificacoes'),

    # Fluxo de Caixa
    path('relatorios/fluxo-caixa/', views.fluxo_caixa, name='fluxo_caixa'),
    path('financeiro/fluxo-caixa/lancar/', views.registrar_movimentacao_manual, name='registrar_movimentacao_manual'),

    # Resumo Operacional (Dashboard)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/exportar/', views.exportar_resumo_operacional, name='exportar_resumo_operacional'),

    # Contas a Receber
    path('contas-receber/', views.contas_receber, name='contas_receber'),
    path('contas-receber/nova/', views.nova_conta_receber, name='nova_conta_receber'),
    path('contas-receber/nova-fiada/', views.nova_venda_fiada, name='nova_venda_fiada'),
    path('contas-receber/receber/<int:conta_id>/', views.registrar_recebimento, name='registrar_recebimento'),
    path('contas-receber/receber-cliente/<int:cliente_id>/', views.registrar_recebimento_cliente, name='registrar_recebimento_cliente'),
    path('contas-receber/deletar/<int:conta_id>/', views.deletar_conta_receber, name='deletar_conta_receber'),
    path('contas-receber/editar/<int:conta_id>/', views.editar_conta_receber, name='editar_conta_receber'),
    path('contas-receber/cancelar/<int:conta_id>/', views.cancelar_conta_receber, name='cancelar_conta_receber'),
    path('contas-receber/detalhe/<int:conta_id>/', views.detalhe_conta_receber, name='detalhe_conta_receber'),
    path('contas-receber/exportar/', views.exportar_contas_receber, name='exportar_contas_receber'),

    # APIs para carrinho e busca
    path('api/produtos/', views.api_buscar_produtos, name='api_buscar_produtos'),
    path('api/produtos/validar-estoque/', views.api_validar_estoque, name='api_validar_estoque'),
    path('api/clientes/', views.api_buscar_clientes, name='api_buscar_clientes'),
    path('api/clientes/<int:cliente_id>/fiado-resumo/', views.api_resumo_cliente_fiado, name='api_resumo_cliente_fiado'),
    path('api/contas-receber/resumo/', views.api_resumo_contas_receber, name='api_resumo_contas_receber'),
    path('produtos/search/', views.api_buscar_produtos, name='search_produtos'),
    path('clientes/search/', views.api_buscar_clientes, name='search_clientes'),
]