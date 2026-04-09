# 💰 Tela: Fluxo de Caixa

## 📍 Localização:

**URL:** `/relatorios/fluxo-caixa/`
**View:** `financeiro.views.fluxo_caixa`
**Template:** `financeiro/fluxo_caixa.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Controlar entradas e saídas de caixa, proporcionando visão clara da movimentação financeira diária/mensal.

## ⚙️ Funcionalidades Principais

### Visão Geral:

Cards informativos:

- **Entradas do Período** - Total de receitas;
- **Saídas do Período** - Total de despesas;
- **Saldo** - Entradas - Saídas;
- **Saldo Acumulado** - Saldo histórico;

### Listagem de Movimentações:

Tabela com:

- Data e Hora;
- Tipo (Entrada/Saída);
- Categoria (Venda/Recebimento/Despesa/Outros);
- Descrição;
- Valor (R$);
- Forma de Pagamento;
- Saldo após movimentação;
- Usuário responsável;

### Lançamento Manual:

Formulário:

- **Tipo*** - Entrada ou Saída;
- **Categoria*** - Select com categorias;
- **Descrição*** - Texto descritivo;
- **Valor (R$)*** - Mínimo 0.01;
- **Data*** - Data da movimentação;
- **Forma de Pagamento*** - Select;
- **Observações** - Campo texto;

### Filtros:

- Período (data início/fim);
- Tipo (Entrada/Saída/Todos);
- Categoria;
- Forma de pagamento;
- Faixa de valores;

### Gráficos:

- **Entradas vs Saídas** - Barras por período;
- **Evolução do Saldo** - Linha temporal;
- **Categorias** - Pizza de distribuição;

## 🔄 Fluxo de Navegação

```
Home → Fluxo de Caixa
   ├─→ Lançar Movimentação Manual → Salvar
   ├─→ Filtrar por Período
   ├─→ Ver Detalhes de Movimentação
   ├─→ Exportar Relatório → PDF/Excel
   └─→ Dashboard Financeiro
```

## 📋 Movimentações Automáticas:

- **Vendas à vista** → Entrada automática;
- **Recebimentos** → Entrada automática;
- Despesas podem ser lançadas manualmente;

## 🎨 Layout:

- Cards de resumo no topo;
- Gráficos interativos;
- Tabela com filtros;
- Badge verde (entrada) / vermelho (saída);
- Formulário em modal;

## 📤 Exportações:

- **PDF:** Relatório completo com gráficos;
- **Excel:** Planilha detalhada de movimentações;
