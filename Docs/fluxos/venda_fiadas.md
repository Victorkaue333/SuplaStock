
## 🔗 Fluxo da Venda Fiada:

```

Cliente seleciona produtos → Carrinho montado
        ↓
  [Nova Venda Fiada]
        ↓
  ┌─ ContaReceber (origem='fiado', status='pendente')
  ├─ ItemContaReceber (1 por produto)
  ├─ Venda (1 por produto, status='Pendente', transacao_id compartilhado)
  └─ Estoque deduzido imediatamente
        ↓
  [Cliente paga depois → Registrar Recebimento]
        ↓
  ┌─ ContaReceber → status='recebido'
  ├─ Pagamento criado para cada Venda → Venda status='Pago'
  └─ Reflete no Dashboard Financeiro e Gestão de Vendas

```