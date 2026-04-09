# 👥 Tela: Gestão de Clientes

## 📍 Localização:

**URL:** `/clientes/`
**View:** `vendas.views.gestao_clientes`
**Template:** `vendas/gestao_clientes.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Gerenciar cadastro completo de clientes, histórico de compras e análise de comportamento.

## ⚙️ Funcionalidades Principais:

### Listagem de Clientes:

Informações exibidas:

- Código do Cliente;
- Nome;
- CPF/CNPJ;
- Telefone;
- Email;
- Total de Compras;
- Última Compra;
- Status (Ativo/Inativo);
- Ações (Ver/Editar/Deletar);

### Cadastro de Cliente:

Campos:

- **Nome*** - Máx 200 caracteres;
- **CPF/CNPJ** - Validação automática;
- **Telefone*** - Formato (XX) XXXXX-XXXX;
- **Email** - Email válido;
- **Endereço** - Rua, número, bairro, cidade, UF, CEP;
- **Data de Nascimento** - DD/MM/AAAA;
- **Observações** - Campo de texto;

### Edição de Cliente:

- Todos os campos editáveis;
- Histórico de alterações;

### Detalhes do Cliente:

Exibe:

- Dados cadastrais completos;
- Histórico de compras;
- Total gasto;
- Ticket médio;
- Produto favorito;
- Contas a receber pendentes;
- Última compra;

### Filtros e Busca:

- Busca por nome/CPF/código;
- Filtro por status;
- Ordenação por nome, compras, último acesso;

## 🔄 Fluxo de Navegação:

```
Home → Gestão de Clientes
   ├─→ Cadastrar Cliente → Salvar
   ├─→ Editar Cliente → Atualizar
   ├─→ Ver Detalhes → Histórico
   ├─→ Tela de Cobrança (se tem dívidas)
   └─→ Exportar Lista → Excel
```

## 📋 Validações:

- ✅ Nome obrigatório;
- ✅ CPF/CNPJ deve ser válido (se preenchido);
- ✅ Telefone obrigatório;
- ✅ Email único (se preenchido);
- ❌ Não permite deletar se tem vendas/contas;

## 🎨 Layout:

- Tabela responsiva com DataTables;
- Cards informativos (Total clientes, Ativos, etc);
- Modal para cadastro/edição;
- Botão flutuante para novo cliente;

## 📤 Exportações:

- **Excel:** Lista completa com ranking de compras;
