import os

base = r'c:\Users\Victor Alves\Documents\GitHub\SuplaStock\suplastock'

replacements = {
    "'login'": "'usuarios:login'",
    "'login_page'": "'usuarios:login_page'",
    "'logout'": "'usuarios:logout'",
    "'recuperar_senha'": "'usuarios:recuperar_senha'",
    "'resetar_senha'": "'usuarios:resetar_senha'",
    "'alterar_senha'": "'usuarios:alterar_senha'",
    "'perfil'": "'usuarios:perfil'",
    "'gestao_produtos'": "'estoque:gestao_produtos'",
    "'cadastrar_produto'": "'estoque:cadastrar_produto'",
    "'editar_produto'": "'estoque:editar_produto'",
    "'deletar_produto'": "'estoque:deletar_produto'",
    "'relatorio_estoque'": "'estoque:relatorio_estoque'",
    "'exportar_estoque_pdf'": "'estoque:exportar_estoque_pdf'",
    "'gestao_vendas'": "'vendas:gestao_vendas'",
    "'registrar_venda'": "'vendas:registrar_venda'",
    "'deletar_venda'": "'vendas:deletar_venda'",
    "'deletar_transacao'": "'vendas:deletar_transacao'",
    "'emitir_nota_fiscal'": "'vendas:emitir_nota_fiscal'",
    "'gestao_clientes'": "'vendas:gestao_clientes'",
    "'cadastrar_cliente'": "'vendas:cadastrar_cliente'",
    "'editar_cliente'": "'vendas:editar_cliente'",
    "'deletar_cliente'": "'vendas:deletar_cliente'",
    "'detalhes_cliente'": "'vendas:detalhes_cliente'",
    "'tela_cobranca'": "'vendas:tela_cobranca'",
    "'tela_cobranca_cliente'": "'vendas:tela_cobranca_cliente'",
    "'registrar_pagamento'": "'vendas:registrar_pagamento'",
    "'relatorios_dashboard'": "'vendas:relatorios_dashboard'",
    "'relatorio_clientes'": "'vendas:relatorio_clientes'",
    "'exportar_vendas_pdf'": "'vendas:exportar_vendas_pdf'",
    "'exportar_vendas_excel'": "'vendas:exportar_vendas_excel'",
    "'exportar_clientes_excel'": "'vendas:exportar_clientes_excel'",
    "'dashboard_financeiro'": "'financeiro:dashboard_financeiro'",
    "'fluxo_caixa'": "'financeiro:fluxo_caixa'",
    "'contas_receber'": "'financeiro:contas_receber'",
    "'nova_conta_receber'": "'financeiro:nova_conta_receber'",
    "'registrar_recebimento'": "'financeiro:registrar_recebimento'",
    "'deletar_conta_receber'": "'financeiro:deletar_conta_receber'",
    "'editar_conta_receber'": "'financeiro:editar_conta_receber'",
    "'cancelar_conta_receber'": "'financeiro:cancelar_conta_receber'",
    "'exportar_contas_receber'": "'financeiro:exportar_contas_receber'",
    "'dashboard'": "'financeiro:dashboard'",
}

# Sort by length (longest first) to avoid partial replacements
sorted_keys = sorted(replacements.keys(), key=len, reverse=True)

dirs_to_scan = [
    os.path.join(base, 'estoque', 'templates'),
    os.path.join(base, 'vendas', 'templates'),
    os.path.join(base, 'financeiro', 'templates'),
    os.path.join(base, 'usuarios', 'templates'),
    os.path.join(base, 'suplastock', 'templates'),
]

count = 0
for d in dirs_to_scan:
    for root, dirs, files in os.walk(d):
        for fname in files:
            if fname.endswith('.html'):
                fpath = os.path.join(root, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                original = content
                for old in sorted_keys:
                    new = replacements[old]
                    # Replace with single quotes
                    content = content.replace("{% url " + old, "{% url " + new)
                    content = content.replace("{%url " + old, "{%url " + new)
                    # Replace with double quotes inside {% url %}
                    old_dq = old.replace("'", '"')
                    new_dq = new.replace("'", '"')
                    content = content.replace('{% url ' + old_dq, '{% url ' + new_dq)
                if content != original:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    count += 1
                    print(f'Updated: {os.path.relpath(fpath, base)}')
print(f'Total files updated: {count}')


