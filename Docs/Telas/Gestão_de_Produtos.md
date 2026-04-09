# 📦 Tela: Gestão de Produtos e Estoque

## 📍 Localização:

**URL:** `/produtos/`
**View:** `estoque.views.gestao_produtos`
**Template:** `estoque/gestao_produtos.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Gestão de Produtos e Estoque** concentra o cadastro, organização e controle dos itens vendidos pela loja, permitindo gerenciamento completo do catálogo e monitoramento de estoque em tempo real.

## ⚙️ Funcionalidades Principais

### Listagem de Produtos:

- Tabela com todos os produtos cadastrados;
- Informações exibidas:
  - Imagem do produto;
  - Nome e Categoria;
  - Fornecedor;
  - Preço de Venda;
  - Custo;
  - Margem (%);
  - Estoque Atual;
  - Estoque Mínimo;
  - Status (Ativo/Zerado/Baixo);
  - Ações (Editar/Deletar);

### Filtros e Busca:

- **Busca por nome** - Campo de texto para busca rápida;
- **Filtro por categoria** - Dropdown com categorias;
- **Filtro por fornecedor** - Dropdown com fornecedores;
- **Filtro por status de estoque** - Todos/Normal/Baixo/Zerado;
- **Ordenação** - Por nome, preço, estoque;

### Cadastro de Produto:

Campos do formulário:

- **Nome*** - Obrigatório, máx 200 caracteres;
- **Categoria*** - Select com categorias cadastradas;
- **Fornecedor*** - Select com fornecedores cadastrados;
- **Custo (R$)*** - Valor de compra, mínimo 0.01;
- **Preço Sugerido (R$)*** - Valor de venda, mínimo 0.01;
- **Margem (%)** - Calculada automaticamente: ((Preço - Custo) / Preço) × 100;
- **Estoque Inicial*** - Quantidade inicial, mínimo 0;
- **Estoque Mínimo*** - Quantidade mínima para alerta, mínimo 0;
- **Data de Validade** - Opcional, formato DD/MM/AAAA;
- **Imagem** - Upload de foto do produto (opcional);
- **Descrição** - Campo de texto longo (opcional);

### Edição de Produto:

- Formulário preenchido com dados atuais;
- Todos os campos editáveis;
- Opção de atualizar imagem;
- Cálculo automático de margem ao alterar custo/preço;
- Validação de estoque (não pode ser negativo);

### Exclusão de Produto:

- Confirmação antes de deletar;
- Verificação de vendas vinculadas;
- Mensagem de alerta se produto tem histórico;

### Alertas de Estoque:

- **Badge Verde** - Estoque normal (acima do mínimo);
- **Badge Amarelo** - Estoque baixo (igual ou próximo ao mínimo);
- **Badge Vermelho** - Estoque zerado;
- **Badge Laranja** - Produto próximo da validade;

### Ações em Massa:

- Seleção múltipla de produtos;
- Exportar selecionados para PDF/Excel;
- Aplicar desconto em lote;
- Atualizar categoria em lote;

## 🔄 Fluxo de Navegação:

```
Home → Gestão de Produtos
   ├─→ Cadastrar Novo Produto
   │    ├─→ Preencher formulário
   │    ├─→ Upload de imagem
   │    └─→ Salvar (volta para listagem)
   │
   ├─→ Editar Produto
   │    ├─→ Modificar dados
   │    └─→ Salvar alterações
   │
   ├─→ Ver Detalhes do Produto
   │    ├─→ Histórico de movimentações
   │    └─→ Vendas relacionadas
   │
   ├─→ Relatório de Estoque
   │    └─→ Exportar PDF/Excel
   │
   └─→ Deletar Produto (com confirmação)
```

## 📋 Validações:

### Cadastro/Edição:

- ✅ Nome não pode ser vazio;
- ✅ Custo deve ser maior que 0;
- ✅ Preço deve ser maior que 0;
- ✅ Preço deve ser maior que custo (aviso);
- ✅ Estoque não pode ser negativo;
- ✅ Estoque mínimo não pode ser negativo;
- ✅ Data de validade deve ser futura;
- ✅ Imagem deve ser JPG, JPEG ou PNG (máx 5MB);
- ✅ Categoria e fornecedor devem existir;

### Exclusão:

- ❌ Não permite deletar se produto tem vendas associadas;
- ⚠️ Aviso se produto tem estoque positivo;

## 🎨 Layout:

- Tabela responsiva com DataTables;
- Botão flutuante para novo produto;
- Cards informativos no topo:
  - Total de produtos;
  - Produtos em estoque baixo;
  - Produtos zerados;
  - Valor total em estoque;
- Badges coloridos para status;
- Modal para cadastro/edição;
- Confirmação de exclusão via SweetAlert;

## 💡 Benefícios:

- ✅ Maior controle sobre disponibilidade de produtos;
- ✅ Redução de perdas por falta de acompanhamento de estoque;
- ✅ Padronização das informações de catálogo;
- ✅ Cálculo automático de margem de lucro;
- ✅ Alertas proativos de reposição;
- ✅ Histórico completo de movimentações;
- ✅ Integração automática com vendas;

## 🔐 Controle de Acesso:

- **Visualização:** Todos os usuários autenticados;
- **Cadastro/Edição:** Todos os usuários autenticados;
- **Exclusão:** Apenas Admin;

## 📱 Responsividade:

- Desktop: Tabela completa com todas as colunas;
- Tablet: Colunas agrupadas, scroll horizontal;
- Mobile: Cards empilhadas com informações principais;

## 🔗 Integrações:

- **Vendas:** Atualiza estoque automaticamente ao registrar venda;
- **Fornecedores:** Vincula produtos aos fornecedores;
- **Categorias:** Organização por categorias;
- **Relatórios:** Geração de relatórios de estoque;
- **Dashboard:** Alimenta KPIs de estoque;

## 📤 Exportações:

- **PDF:** Relatório completo de estoque com filtros aplicados;
- **Excel:** Planilha com todos os campos para análise;