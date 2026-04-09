# 💳 Tela: Contas a Receber

## 📍 Localização:

**URL:** `/contas-receber/`
**View:** `financeiro.views.contas_receber`
**Template:** `financeiro/contas_receber.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Contas a Receber** permite acompanhar e gerenciar valores pendentes de clientes, facilitando o controle financeiro, fluxo de caixa e redução de inadimplência.

## ⚙️ Funcionalidades Principais

### Listagem de Contas:

- Tabela com todas as contas a receber
- Informações exibidas:
  - ID da Conta;
  - Cliente (Nome/Código);
  - Descrição;
  - Valor Original (R$);
  - Valor Pago (R$);
  - Saldo Restante (R$);
  - Data de Vencimento;
  - Status (Pendente/Pago/Vencido/Cancelado);
  - Tipo (Avulsa/Fiada);
  - Ações (Ver/Receber/Editar/Cancelar/Deletar);

### Cards Informativos:

- **Total a Receber** - Soma de todas as contas pendentes;
- **Vencidas** - Valor total vencido (em vermelho);
- **A Vencer** - Valor a vencer nos próximos dias;
- **Recebido no Mês** - Total já recebido no mês atual;
- **Número de Clientes com Dívidas** - Quantidade de devedores;

### Filtros e Busca:

- **Cliente** - Busca por nome/código;
- **Status** - Todos/Pendente/Pago/Vencido/Cancelado;
- **Tipo** - Todos/Avulsa/Fiada;
- **Período de Vencimento** - Data início e fim;
- **Valor Mínimo/Máximo** - Filtro por faixa;
- **Ordenação** - Por vencimento, valor, cliente;

### Nova Conta Avulsa:

Formulário:

- **Cliente*** - Select com clientes cadastrados;
- **Descrição*** - Texto descritivo (ex: "Crédito de compras");
- **Valor (R$)*** - Valor total, mínimo 0.01;
- **Data de Vencimento*** - Data futura recomendada;
- **Observações** - Campo de texto opcional;

Fluxo:

1. Preencher formulário;
2. Validar dados;
3. Salvar conta;
4. Conta criada com status "Pendente";

### Nova Venda Fiada (com Carrinho):

Multi-step:

#### Etapa 1: Selecionar Cliente:

- Busca de cliente;
- Verificar limite de crédito (se configurado);
- Visualizar dívidas existentes do cliente;

#### Etapa 2: Adicionar Produtos:

- Busca de produtos (autocomplete);
- Validação de estoque;
- Carrinho de compras:
  - Adicionar/remover itens;
  - Alterar quantidades;
  - Visualizar preços;
  - Calcular subtotais;
  - Total geral;

#### Etapa 3: Definir Condições:

- **Data de Vencimento*** - Padrão: 30 dias;
- **Desconto** - Opcional (R$ ou %);
- **Observações** - Campo de texto;

#### Etapa 4: Confirmar:

- Resumo da venda fiada;
- Botão "Criar Venda Fiada";
- Atualiza estoque automaticamente;
- Cria conta a receber vinculada;

### Registrar Recebimento:

Formulário:

- **Valor Recebido (R$)*** - Máximo: Saldo restante;
- **Data do Recebimento*** - Padrão: Hoje;
- **Forma de Pagamento*** - Dinheiro/Débito/Crédito/PIX/Transferência;
- **Observações** - Campo de texto;
- **Recebimento Parcial** - Checkbox;

Comportamento:

- Se valor = saldo total → Status: "Pago";
- Se valor < saldo total → Status: "Pendente" (parcial);
- Registra histórico de pagamentos;
- Atualiza saldo automaticamente;

### Editar Conta:

Campos editáveis:

- Descrição;
- Valor original (se ainda não houver pagamentos);
- Data de vencimento;
- Observações;

**Restrições:**

- Não permite editar se já foi pago;
- Não permite editar valor se já teve pagamento parcial;

### Cancelar Conta:

- Confirmação obrigatória;
- Motivo do cancelamento (opcional);
- Altera status para "Cancelado";
- Se for venda fiada → Opção de estornar estoque;
- Não exclui, apenas marca como cancelada;

### Deletar Conta:

- Apenas Admin;
- Confirmação obrigatória;
- Remove permanentemente do banco;
- Só permite se não houver pagamentos registrados;

### Detalhes da Conta:

Exibe:

- Informações completas da conta;
- Dados do cliente (com botão para ver perfil);
- Histórico de pagamentos (se houver):
  - Data;
  - Valor;
  - Forma de pagamento;
  - Usuário que registrou;
- Se for venda fiada: Lista de produtos;
- Linha do tempo de alterações;
- Botões de ação contextuais;

### Alertas e Notificações:

- **Badge Vermelho** - Conta vencida;
- **Badge Amarelo** - Vence em até 7 dias;
- **Badge Verde** - Pago;
- **Badge Cinza** - Cancelado;
- Notificação de vencimento próximo;
- Destaque para clientes com múltiplas dívidas;

## 🔄 Fluxo de Navegação:

```
Home → Contas a Receber
   ├─→ Nova Conta Avulsa
   │    ├─→ Preencher dados
   │    └─→ Salvar
   │
   ├─→ Nova Venda Fiada
   │    ├─→ Selecionar Cliente
   │    ├─→ Adicionar Produtos
   │    ├─→ Definir Vencimento
   │    └─→ Confirmar (cria conta)
   │
   ├─→ Ver Detalhes da Conta
   │    ├─→ Visualizar histórico
   │    ├─→ Registrar Recebimento
   │    ├─→ Editar Conta
   │    └─→ Cancelar/Deletar
   │
   ├─→ Registrar Recebimento
   │    ├─→ Informar valor e forma
   │    └─→ Confirmar (atualiza conta)
   │
   ├─→ Filtrar Contas
   │    └─→ Aplicar filtros
   │
   └─→ Exportar
        ├─→ PDF
        └─→ Excel
```

## 📋 Validações:

### Nova Conta:

- ✅ Cliente deve ser selecionado;
- ✅ Valor deve ser maior que 0;
- ✅ Data de vencimento não pode ser muito antiga;
- ✅ Descrição não pode ser vazia;

### Venda Fiada:

- ✅ Cliente deve ser selecionado;
- ✅ Carrinho deve ter ao menos 1 produto;
- ✅ Quantidade não pode exceder estoque;
- ✅ Data de vencimento deve ser futura;
- ⚠️ Aviso se cliente já tem dívidas vencidas;

### Recebimento:

- ✅ Valor deve ser maior que 0;
- ✅ Valor não pode exceder saldo restante;
- ✅ Data do recebimento não pode ser futura;
- ✅ Forma de pagamento deve ser selecionada;

### Edição:

- ❌ Não permite editar conta paga;
- ⚠️ Aviso ao alterar valor se já houver pagamentos;

### Cancelamento:

- ⚠️ Confirmação obrigatória;
- ⚠️ Explicar impacto (não pode ser desfeito);

## 🎨 Layout:

- Cards informativos no topo com KPIs;
- Tabela responsiva com DataTables;
- Badges coloridos para status;
- Botões de ação contextuais;
- Modal para registrar recebimento;
- Formulário multi-step para venda fiada;
- Timeline para histórico de pagamentos;
- Gráfico de vencimentos futuros (opcional);

## 💡 Benefícios:

- ✅ Melhor previsibilidade de recebimentos;
- ✅ Redução de inadimplência com acompanhamento contínuo;
- ✅ Apoio à tomada de decisão financeira;
- ✅ Histórico completo de pagamentos;
- ✅ Facilita cobrança com visualização clara de dívidas;
- ✅ Integração com vendas (fiado);
- ✅ Alertas proativos de vencimentos;


## 🔐 Controle de Acesso:

- **Visualização:** Todos os usuários autenticados;
- **Criar/Editar:** Todos os usuários autenticados;
- **Registrar Recebimento:** Todos os usuários autenticados;
- **Cancelar:** Todos os usuários autenticados;
- **Deletar:** Apenas Admin;

## 📱 Responsividade:

- Desktop: Tabela completa;
- Tablet: Colunas essenciais, scroll horizontal;
- Mobile: Cards empilhados;

## 🔗 Integrações:

- **Clientes:** Vincula contas aos clientes;
- **Vendas:** Cria conta automaticamente em venda fiada;
- **Estoque:** Atualiza ao criar venda fiada;
- **Fluxo de Caixa:** Registra entrada ao receber;
- **Dashboard:** Alimenta KPIs financeiros;
- **Tela de Cobrança:** Integração para cobrança por cliente;

## 📤 Exportações:

- **PDF:** Relatório de contas com filtros aplicados;
- **Excel:** Planilha com todos os campos;
- **Recibo:** PDF individual por recebimento;