# 💰 Tela: Dashboard Financeiro

## 📍 Localização:

**URL:** `/financeiro/`
**View:** `financeiro.views.dashboard_financeiro`
**Template:** `financeiro/dashboard_financeiro.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Dashboard Financeiro** oferece uma visão consolidada da saúde financeira da loja, apoiando análises rápidas e decisões estratégicas com gráficos, KPIs e análises detalhadas.

## ⚙️ Funcionalidades Principais:

### KPIs Financeiros:

- **Faturamento Total** - Valor total de vendas no período;
- **Lucro Bruto** - Faturamento - Custos dos produtos;
- **Margem Média** - Percentual médio de lucro;
- **Recebimentos** - Total recebido no período;
- **Contas a Receber** - Pendências totais;
- **Inadimplência** - Valores vencidos;
- **Ticket Médio** - Valor médio por venda;
- **ROI** - Retorno sobre investimento;

### Gráficos e Visualizações:

#### 1. Evolução de Vendas (Linha):

- Faturamento diário/semanal/mensal;
- Comparativo com período anterior;
- Linha de tendência;
- Marcadores de picos e quedas;

#### 2. Fluxo de Caixa (Barras):

- Entradas vs Saídas por período;
- Separação por forma de pagamento;
- Saldo acumulado;
- Projeções futuras;

#### 3. Produtos Mais Vendidos (Pizza/Barras):

- Top 10 produtos por faturamento;
- Top 10 produtos por quantidade;
- Percentual de cada produto no total;

#### 4. Vendas por Categoria (Pizza):

- Distribuição do faturamento por categoria;
- Comparativo de períodos;

#### 5. Formas de Pagamento (Pizza):

- Distribuição: Dinheiro/Cartão/PIX/Fiado;
- Percentual de cada forma;

#### 6. Margem de Lucro (Gauge):

- Margem média percentual;
- Indicador visual (verde/amarelo/vermelho);
- Meta vs Realizado;

### Filtros e Períodos:

- **Período Customizado** - Data início e fim;
- **Períodos Rápidos:**
  - Hoje;
  - Ontem;
  - Últimos 7 dias;
  - Últimos 30 dias;
  - Mês atual;
  - Mês anterior;
  - Ano atual;
- **Comparar com período anterior** - Toggle on/off

### Análises Detalhadas:

#### Produtos:

- **Mais Vendidos** - Por valor e quantidade;
- **Menos Vendidos** - Produtos parados;
- **Maior Margem** - Produtos mais lucrativos;
- **Menor Margem** - Produtos com lucro baixo;

#### Clientes:

- **Top Clientes** - Maiores compradores;
- **Clientes Inativos** - Sem compras no período;
- **Ticket Médio por Cliente** - Análise de comportamento;

#### Tendências:

- **Dias da Semana** - Melhores dias para vendas;
- **Horários de Pico** - Períodos de maior movimento;
- **Sazonalidade** - Variações mensais;

### Ações Rápidas:

- **Exportar Dashboard** - PDF com todos os gráficos;
- **Relatórios Gerenciais** - Acesso a relatórios detalhados;
- **Fluxo de Caixa** - Link direto;
- **Contas a Receber** - Link direto;

## 🔄 Fluxo de Navegação

```
Home → Dashboard Financeiro
   ├─→ Selecionar Período
   ├─→ Analisar Gráficos
   ├─→ Ver Produto Específico
   │    └─→ Histórico de Vendas do Produto
   ├─→ Ver Cliente Específico
   │    └─→ Histórico de Compras
   ├─→ Acessar Fluxo de Caixa
   ├─→ Acessar Contas a Receber
   ├─→ Exportar Dashboard (PDF)
   └─→ Relatórios Gerenciais
```

## 📋 Dados Calculados:

### Fórmulas:

- **Lucro Bruto:** Σ(Preço Venda - Custo) × Quantidade;
- **Margem (%):** ((Preço - Custo) / Preço) × 100;
- **Ticket Médio:** Faturamento Total / Número de Vendas;
- **ROI (%):** (Lucro / Investimento) × 100;
- **Taxa de Inadimplência:** Valores Vencidos / Total a Receber × 100;

### Períodos de Comparação:

- Crescimento/Queda percentual vs período anterior;
- Indicadores visuais (▲/▼) com cores;

## 🎨 Layout:

- Grid responsivo de cards com KPIs;
- Gráficos interativos (Chart.js);
- Cores consistentes:
  - Verde: Positivo, crescimento;
  - Vermelho: Negativo, queda, alerta;
  - Azul: Neutro, informação;
  - Amarelo: Atenção;
- Tooltips nos gráficos;
- Tabelas de ranking com badges;

## 💡 Benefícios:

- ✅ Monitoramento financeiro em tempo real;
- ✅ Detecção rápida de tendências e desvios;
- ✅ Melhoria no planejamento e na previsibilidade do negócio;
- ✅ Identificação de produtos/categorias mais lucrativos;
- ✅ Análise de comportamento de clientes;
- ✅ Suporte à tomada de decisão estratégica;
- ✅ Visão consolidada sem necessidade de relatórios complexos;

## 🔐 Controle de Acesso:

- **Visualização:** Todos os usuários autenticados;
- **Dados Sensíveis:** Admin vê custos e margens / Operação vê apenas faturamento;
- **Exportação:** Todos os usuários autenticados;

## 📱 Responsividade:

- Desktop: Grid de 2-3 colunas, gráficos lado a lado;
- Tablet: 2 colunas, gráficos empilhados;
- Mobile: 1 coluna, gráficos simplificados;

## 🔗 Integrações:

- **Vendas:** Alimenta todos os KPIs de vendas;
- **Estoque:** Calcula margem baseada em custos;
- **Contas a Receber:** Valores pendentes e inadimplência;
- **Fluxo de Caixa:** Entradas e saídas;

## 📤 Exportações:

- **PDF:** Dashboard completo com todos os gráficos;
- **Excel:** Dados brutos para análises customizadas;
