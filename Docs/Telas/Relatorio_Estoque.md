# 📋 Tela: Relatório de Estoque

## 📍 Localização:

**URL:** `/relatorios/estoque/`
**View:** `estoque.views.relatorio_estoque`
**Template:** `estoque/relatorio_estoque.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Fornecer análise detalhada do estoque com alertas, estatísticas e suporte à tomada de decisão sobre reposição.

## ⚙️ Funcionalidades Principais:

### Cards de Resumo:

- **Total de Produtos** - Quantidade de SKUs cadastrados;
- **Produtos em Estoque** - Itens com quantidade > 0;
- **Produtos Zerados** - Itens sem estoque;
- **Produtos em Estoque Baixo** - Abaixo do mínimo;
- **Valor Total em Estoque** - Soma (Quantidade × Custo);

### Relatório Detalhado:

Tabela com:

- Imagem;
- Nome do Produto;
- Categoria;
- Fornecedor;
- Estoque Atual;
- Estoque Mínimo;
- Status (Normal/Baixo/Zerado);
- Valor Unitário (Custo);
- Valor Total em Estoque;
- Última Movimentação;
- Ação (Ver Detalhes/Editar);

### Alertas Visuais:

- 🟢 **Verde:** Estoque normal (acima do mínimo);
- 🟡 **Amarelo:** Estoque baixo (igual ou próximo ao mínimo);
- 🔴 **Vermelho:** Estoque zerado;
- 🟠 **Laranja:** Próximo da validade (< 30 dias);

### Filtros:

- **Categoria** - Filtrar por categoria específica;
- **Fornecedor** - Filtrar por fornecedor;
- **Status de Estoque** - Normal/Baixo/Zerado;
- **Validade** - Produtos próximos da validade;
- **Ordenação** - Por nome, estoque, valor;

### Análises:

- **Produtos Mais Vendidos** - Top 10 com maior giro;
- **Produtos Parados** - Sem movimentação em X dias;
- **Giro de Estoque** - Taxa de rotação;
- **Sugestões de Reposição** - Lista priorizada;

### Ações em Massa:

- Marcar produtos para pedido de reposição;
- Exportar lista de reposição;
- Atualizar estoque mínimo em lote;

## 🔄 Fluxo de Navegação:

```
Home → Relatório de Estoque
   ├─→ Visualizar Análise Completa
   ├─→ Filtrar por Status/Categoria
   ├─→ Ver Produto em Alerta
   │    └─→ Editar Estoque/Mínimo
   ├─→ Gerar Lista de Reposição
   └─→ Exportar Relatório
        ├─→ PDF (completo com alertas)
        └─→ Excel (planilha para análise)
```

## 📊 Análises Calculadas

### Giro de Estoque:

```
Giro = Quantidade Vendida (período) / Estoque Médio
```

### Valor em Estoque:

```
Valor Total = Σ(Quantidade × Custo Unitário)
```

### Cobertura de Estoque:

```
Dias de Cobertura = Estoque Atual / Venda Média Diária
```

## 🎨 Layout:

- Cards de KPIs no topo;
- Tabela responsiva com DataTables;
- Badges coloridos para status;
- Gráficos de distribuição (opcional):
  - Pizza por categoria;
  - Barras por fornecedor;
- Seção de alertas destacada;

## 💡 Benefícios:

- ✅ Identificação rápida de produtos críticos;
- ✅ Planejamento de reposição baseado em dados;
- ✅ Redução de perdas por validade;
- ✅ Otimização do capital em estoque;
- ✅ Evita ruptura de produtos populares;

## 📤 Exportações

### PDF:

- Relatório completo formatado;
- Alertas destacados;
- Gráficos incluídos;
- Logo da loja;

### Excel:

- Planilha com todos os campos;
- Formatação condicional para alertas;
- Cálculos automáticos;
- Pronto para análise;

## 🔐 Controle de Acesso:

- Visualização: Todos os usuários;
- Edição de estoque: Todos os usuários;
- Valores de custo: Visível apenas para Admin;

## 📱 Responsividade:

- Desktop: Tabela completa;
- Mobile: Cards resumidos, tabela simplificada;
