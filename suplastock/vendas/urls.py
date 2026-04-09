from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    # Gestão de Vendas
    path('vendas/', views.gestao_vendas, name='gestao_vendas'),
    path('vendas/registrar/', views.registrar_venda, name='registrar_venda'),
    path('vendas/editar_transacao/<str:transacao_id>/', views.editar_transacao, name='editar_transacao'),
    path('vendas/deletar/<int:venda_id>/', views.deletar_venda, name='deletar_venda'),
    path('vendas/deletar_transacao/<str:transacao_id>/', views.deletar_transacao, name='deletar_transacao'),

    # Nota Fiscal
    path('notas-fiscais/emitir/', views.emitir_nota_fiscal, name='emitir_nota_fiscal'),

    # Gestão de Clientes
    path('clientes/', views.gestao_clientes, name='gestao_clientes'),
    path('clientes/cadastrar/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('clientes/editar/<int:cliente_id>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/deletar/<int:cliente_id>/', views.deletar_cliente, name='deletar_cliente'),
    path('clientes/detalhes/<int:cliente_id>/', views.detalhes_cliente, name='detalhes_cliente'),

    # Cobrança
    path('cobranca/', views.tela_cobranca, name='tela_cobranca'),
    path('cobranca/<int:cliente_id>/', views.tela_cobranca, name='tela_cobranca_cliente'),
    path('pagamento/registrar/', views.registrar_pagamento, name='registrar_pagamento'),

    # Relatórios
    path('relatorios/', views.relatorios_dashboard, name='relatorios_dashboard'),
    path('relatorios/clientes/', views.relatorio_clientes, name='relatorio_clientes'),

    # Exportação
    path('export/vendas/pdf/', views.exportar_vendas_pdf, name='exportar_vendas_pdf'),
    path('export/vendas/excel/', views.exportar_vendas_excel, name='exportar_vendas_excel'),
    path('export/clientes/excel/', views.exportar_clientes_excel, name='exportar_clientes_excel'),
]
