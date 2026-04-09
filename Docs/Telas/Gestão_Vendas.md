# 🛒 Tela: Gestão de Vendas

## 📍 Localização:

**URL:** `/vendas/`
**View:** `vendas.views.gestao_vendas`
**Template:** `vendas/gestao_vendas.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Gestão de Vendas** controla o ciclo de vendas da operação, do registro da transação ao acompanhamento de resultados, fornecendo histórico completo e rastreabilidade de todas as vendas realizadas.

## ⚙️ Funcionalidades Principais:

### Listagem de Vendas:

- Tabela com histórico completo de vendas;
- Informações exibidas:
  - ID da Transação;
  - Data e Hora;
  - Cliente;
  - Produtos vendidos (resumo);
  - Quantidade total de itens;
  - Valor Total (R$);
  - Forma de Pagamento;
  - Status (Pago/Pendente/Cancelado);
  - Ações (Ver Detalhes/Editar/Deletar/Nota Fiscal);

### Filtros e Busca:

- **Período** - Data inicial e final;
- **Cliente** - Busca por nome/código;
- **Status** - Filtro por status de pagamento;
- **Forma de Pagamento** - Dinheiro/Cartão/PIX/Fiado;
- **Valor Mínimo/Máximo** - Filtro por faixa de valores;
- **Ordenação** - Por data (recente/antigo), valor (maior/menor);

### Registro de Nova Venda:

#### Etapa 1: Selecionar Cliente:

- Busca por nome/CPF/código;
- Opção "Consumidor Final" para venda sem cadastro;
- Botão para cadastrar novo cliente;

#### Etapa 2: Adicionar Produtos ao Carrinho:

Campos:

- **Busca de Produto** - Autocomplete com nome/código;
- **Quantidade*** - Mínimo 1, máximo = estoque disponível;
- **Preço Unitário** - Exibido automaticamente, editável;
- **Subtotal** - Calculado automaticamente (quantidade × preço);

Carrinho exibido:

- Lista de produtos adicionados;
- Botão remover item;
- Botão editar quantidade;
- Total parcial;
- Total geral;

#### Etapa 3: Definir Pagamento:

- **Forma de Pagamento*** - Select (Dinheiro/Débito/Crédito/PIX/Fiado);
- **Valor Pago** - Campo numérico;
- **Troco** - Calculado automaticamente se Dinheiro;
- **Desconto** - Opcional (valor ou %);
- **Observações** - Campo de texto;

#### Etapa 4: Confirmação:

- Resumo da venda;
- Total de itens;
- Valor total;
- Botão "Finalizar Venda";
- Opção "Emitir Nota Fiscal";

### Edição de Transação:

- Permite editar vendas existentes;
- Modificar produtos, quantidades e valores;
- Alterar forma de pagamento;
- Adicionar/remover itens do carrinho;
- **Atenção:** Estoque é recalculado ao salvar;

### Detalhes da Venda:

- Informações completas da transação;
- Lista de todos os produtos;
- Dados do cliente;
- Forma de pagamento e valores;
- Histórico de alterações (se houver);
- Opção de reimprimir nota fiscal;

### Exclusão de Venda:

- Confirmação obrigatória;
- Estorna o estoque dos produtos;
- Registra log de exclusão;
- Apenas Admin pode deletar vendas antigas;

### Emissão de Nota Fiscal:

- Geração de PDF com dados da venda;
- Informações da loja;
- Dados do cliente;
- Detalhamento dos produtos;
- Totais e forma de pagamento;
- Número sequencial da nota;

## 🔄 Fluxo de Navegação:

```
Home → Gestão de Vendas
   ├─→ Registrar Nova Venda
   │    ├─→ Selecionar Cliente
   │    ├─→ Adicionar Produtos ao Carrinho
   │    ├─→ Definir Forma de Pagamento
   │    ├─→ Confirmar Venda
   │    └─→ Emitir Nota Fiscal (opcional)
   │
   ├─→ Ver Detalhes da Venda
   │    ├─→ Visualizar produtos
   │    ├─→ Reimprimir Nota Fiscal
   │    └─→ Editar Transação
   │
   ├─→ Editar Transação
   │    ├─→ Modificar itens
   │    └─→ Salvar alterações
   │
   ├─→ Deletar Venda (Admin)
   │    └─→ Confirmar exclusão
   │
   └─→ Exportar Relatório
        ├─→ PDF
        └─→ Excel
```

## 📋 Validações:

### Registro de Venda:

- ✅ Deve ter ao menos 1 produto no carrinho;
- ✅ Quantidade não pode exceder estoque disponível;
- ✅ Preço unitário deve ser maior que 0;
- ✅ Forma de pagamento deve ser selecionada;
- ✅ Valor pago (se não for fiado) deve ser ≥ valor total;
- ✅ Cliente deve ser selecionado;
- ✅ Estoque é atualizado automaticamente;

### Edição:

- ⚠️ Aviso se venda já foi faturada;
- ⚠️ Validação de estoque ao adicionar novos produtos;
- ⚠️ Recalcula totais automaticamente;

### Exclusão:

- ❌ Bloqueia exclusão se nota fiscal já foi emitida (apenas Admin);
- ✅ Estorna estoque automaticamente;
- ✅ Registra log de auditoria;

## 🎨 Layout:

- Tabela responsiva com paginação;
- Cards informativos no topo:
  - Vendas do Dia;
  - Vendas do Mês;
  - Ticket Médio;
  - Total de Vendas;
- Formulário multi-step para nova venda;
- Carrinho de compras interativo;
- Modal para detalhes da venda;
- Badges coloridos para status;
- Botão flutuante para nova venda;

## 💡 Benefícios:

- ✅ Rastreabilidade completa das vendas;
- ✅ Agilidade no atendimento e no fechamento de pedidos;
- ✅ Dados confiáveis para análise comercial e financeira;
- ✅ Integração automática com estoque;
- ✅ Controle de formas de pagamento;
- ✅ Histórico detalhado por cliente;
- ✅ Emissão rápida de nota fiscal;

## 🔐 Controle de Acesso:

- **Visualização:** Todos os usuários autenticados;
- **Registro:** Todos os usuários autenticados;
- **Edição:** Todos os usuários (até 24h após venda) / Admin (sem limite);
- **Exclusão:** Apenas Admin;

## 📱 Responsividade:

- Desktop: Tabela completa com todas as colunas;
- Tablet: Colunas essenciais, scroll horizontal;
- Mobile: Cards empilhados com informações resumidas;

## 🔗 Integrações:

- **Estoque:** Atualiza automaticamente ao registrar/editar/deletar venda;
- **Clientes:** Vincula venda ao cliente, histórico de compras;
- **Financeiro:** Alimenta contas a receber (se fiado) ou fluxo de caixa;
- **Dashboard:** KPIs de vendas em tempo real;
- **Nota Fiscal:** Geração automática de PDF;

## 📤 Exportações:

- **PDF:** Relatório de vendas com filtros aplicados;
- **Excel:** Planilha detalhada com todas as vendas;
- **Nota Fiscal:** PDF individual por venda;

## 📊 Relatórios Gerados:

- Vendas por período;
- Vendas por cliente;
- Vendas por produto;
- Vendas por forma de pagamento;
- Ranking de produtos mais vendidos;
- Ticket médio por cliente;