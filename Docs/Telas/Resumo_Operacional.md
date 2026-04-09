# 📊 Tela: Resumo Operacional (Dashboard)

## 📍 Localização:

**URL:** `/dashboard/`
**View:** `financeiro.views.dashboard`
**Template:** `financeiro/dashboard.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Resumo Operacional** apresenta indicadores essenciais da rotina da loja em um único painel, facilitando a leitura rápida do cenário atual. Dashboard principal para tomada de decisões operacionais.

## ⚙️ Funcionalidades Principais

### KPIs Principais:

- **Vendas do Dia** - Valor total de vendas no dia atual;
- **Vendas do Mês** - Faturamento acumulado no mês;
- **Lucro Estimado** - Margem de lucro com base nos custos;
- **Produtos em Estoque** - Total de itens disponíveis;
- **Clientes Ativos** - Clientes com compras recentes;
- **Contas a Receber** - Total pendente de recebimento;

### Indicadores Visuais:

- **Produtos com Estoque Baixo** - Alerta para produtos próximos ao mínimo;
- **Produtos Zerados** - Lista de itens sem estoque;
- **Vendas Recentes** - Últimas 10 transações;
- **Top Produtos** - Produtos mais vendidos do período;

### Filtros e Período:

- Seleção de período (Dia/Semana/Mês/Ano);
- Comparativo com período anterior;
- Gráfico de evolução de vendas;

### Ações Rápidas:

- **Nova Venda** - Botão de acesso rápido;
- **Registrar Recebimento** - Pagamento de conta;
- **Ver Relatórios** - Acesso aos relatórios completos;
- **Exportar** - Download do resumo em PDF/Excel;

## 🔄 Fluxo de Navegação:

```
Home → Dashboard (Resumo Operacional)
   ├─→ Ver detalhes de venda específica
   ├─→ Acessar produto com estoque baixo
   ├─→ Abrir Dashboard Financeiro
   ├─→ Nova Venda
   └─→ Exportar Resumo
```

## 📋 Dados Exibidos:

### Cards Superiores:

1. **Caixa de Vendas do Dia**:
   - Valor total;
   - Quantidade de transações;
   - Comparativo com dia anterior;

2. **Vendas do Mês**
   - Faturamento mensal;
   - Ticket médio;
   - Meta vs Realizado;

3. **Lucro Estimado**
   - Margem percentual;
   - Valor absoluto;
   - Comparativo mensal;

4. **Contas a Receber**
   - Total pendente;
   - Vencidas;
   - A vencer;

### Tabelas e Listas:

- **Vendas Recentes** (ID, Data, Cliente, Valor, Status);
- **Produtos em Alerta** (Nome, Estoque Atual, Estoque Mínimo);
- **Produtos Zerados** (Nome, Categoria, Último Movimento);

## 🎨 Layout:

- Grid responsivo de cards com KPIs;
- Tabelas com paginação;
- Badges coloridos para status;
- Ícones FontAwesome;;
- Cores de alerta para estoques críticos;

## 💡 Benefícios:

- ✅ Priorização rápida das ações do dia;
- ✅ Melhor acompanhamento da eficiência operacional;
- ✅ Suporte à tomada de decisão com base em indicadores;
- ✅ Visão consolidada sem necessidade de navegar entre telas;
- ✅ Identificação imediata de problemas (estoque, vendas);

## 🔐 Controle de Acesso:

- Todos os usuários autenticados têm acesso;
- Dados filtrados por permissão (Admin vê tudo, Operação vê apenas seu escopo);

## 📱 Responsividade:

- Desktop: Grid de 4 colunas;
- Tablet: Grid de 2 colunas;
- Mobile: 1 coluna com cards empilhados;

## 📈 Métricas Calculadas:

- **Ticket Médio:** Valor total de vendas ÷ Quantidade de vendas;
- **Margem de Lucro:** (Preço Venda - Custo) ÷ Preço Venda × 100;
- **Taxa de Conversão:** Vendas realizadas ÷ Clientes ativos;