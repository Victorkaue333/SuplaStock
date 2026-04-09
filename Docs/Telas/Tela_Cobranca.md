# 🧾 Tela: Tela de Cobrança

## 📍 Localização:

**URL:** `/cobranca/` ou `/cobranca/<cliente_id>/`
**View:** `vendas.views.tela_cobranca`
**Template:** `vendas/tela_cobranca.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Facilitar a cobrança de clientes com dívidas, centralizando informações de débitos por cliente e permitindo registro rápido de pagamentos.

## ⚙️ Funcionalidades Principais:

### Visão Geral:

Cards informativos:

- **Total de Clientes com Dívidas** - Quantidade;
- **Total a Receber Geral** - Soma de todas as dívidas;
- **Vencidas** - Valor total vencido;
- **A Vencer Hoje** - Cobranças urgentes;

### Listagem de Clientes Devedores:

Informações:

- Nome do Cliente;
- CPF/Telefone;
- Total de Dívidas (R$);
- Quantidade de Contas;
- Valor Vencido;
- Próximo Vencimento;
- Status (Regular/Atrasado/Crítico);
- Ação (Ver Dívidas/Cobrar);

### Detalhes por Cliente:

Ao selecionar um cliente:

- Dados de contato destacados;
- Histórico de compras;
- Lista de todas as contas pendentes:
  - Descrição;
  - Valor original;
  - Valor pago;
  - Saldo restante;
  - Data de vencimento;
  - Dias em atraso;
  - Botão "Receber";

### Registro Rápido de Pagamento:

Modal simplificado:

- Cliente já selecionado;
- Múltiplas contas do cliente visíveis;
- **Valor a Receber*** - Input;
- **Forma de Pagamento*** - Select;
- **Observações** - Texto;
- Botão "Registrar Pagamento";

Comportamento:

- Pode quitar uma conta específica;
- Pode fazer pagamento geral (distribui entre contas);
- Atualiza saldos automaticamente;

### Filtros:

- Busca por nome/CPF;
- Status (Todos/Regular/Atrasado/Crítico);
- Ordenar por valor/vencimento;

### Ações em Massa:

- Enviar lembrete por WhatsApp (futura);
- Gerar relatório de cobranças;
- Exportar lista de devedores;

## 🔄 Fluxo de Navegação:

```
Home → Tela de Cobrança
   ├─→ Ver Clientes Devedores
   ├─→ Selecionar Cliente
   │    ├─→ Ver Dívidas Detalhadas
   │    └─→ Registrar Pagamento
   │         └─→ Confirmar (atualiza conta)
   │
   ├─→ Acessar Perfil do Cliente
   ├─→ Nova Venda para Cliente
   └─→ Exportar Lista → PDF/Excel
```

## 🎨 Layout:

- Cards de KPIs no topo;
- Lista de clientes com badges de status;
- Painel lateral com detalhes ao selecionar;
- Cores de alerta:
  - 🟢 Verde: Regular (sem atrasos);
  - 🟡 Amarelo: Atenção (vence em < 7 dias);
  - 🔴 Vermelho: Crítico (vencido);
- Modal de pagamento rápido;

## 💡 Benefícios:

- ✅ Visão consolidada de cobranças;
- ✅ Priorização de cobranças urgentes;
- ✅ Registro rápido de recebimentos;
- ✅ Redução de inadimplência;
- ✅ Melhor relacionamento com o cliente;

## 🔐 Controle de Acesso:

- Todos os usuários autenticados;
- Registros de quem fez cada cobrança;

## 📱 Responsividade:

- Desktop: Layout de 2 colunas (lista + detalhes);
- Mobile: Lista com detalhes em modal;

## 🔗 Integrações:

- **Contas a Receber:** Busca dívidas automaticamente;
- **Clientes:** Exibe dados de contato;
- **Fluxo de Caixa:** Registra entrada ao receber;
