# 🏠 Tela: Acesso Rápido (Home)

## 📍 Localização:

**URL:** `/home/`
**Template:** `base/home.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

A tela de **Acesso Rápido** centraliza os atalhos das funcionalidades mais usadas no dia a dia da operação, reduzindo cliques e acelerando tarefas recorrentes. É a primeira tela exibida após o login.

## ⚙️ Funcionalidades Principais:

### Cards de Acesso Rápido:

- **Dashboard** - Resumo operacional do dia
- **Nova Venda** - Registro rápido de venda
- **Gestão de Produtos** - Acesso ao catálogo de produtos
- **Gestão de Clientes** - Lista de clientes cadastrados
- **Contas a Receber** - Gestão de contas pendentes
- **Dashboard Financeiro** - Visão financeira consolidada
- **Relatórios** - Acesso aos relatórios do sistema
- **Perfil** - Configurações do usuário

### Informações Exibidas:

- Nome do usuário logado
- Papel/Permissão (Admin ou Operação)
- Ícones visuais para cada funcionalidade
- Navegação direta para cada módulo

## 🔄 Fluxo de Navegação

```
Login → Home (Acesso Rápido)
   ├─→ Dashboard (Resumo Operacional)
   ├─→ Registrar Venda
   ├─→ Gestão de Produtos
   ├─→ Gestão de Clientes
   ├─→ Contas a Receber
   ├─→ Dashboard Financeiro
   ├─→ Relatórios
   └─→ Perfil
```

## 🎨 Layout:

- Grid responsivo com cards clicáveis;
- Ícones FontAwesome para cada funcionalidade;
- Cores diferenciadas para cada módulo;
- Sidebar com logo e informações do usuário;

## 💡 Benefícios:

- ✅ Menor tempo para executar rotinas;
- ✅ Melhor fluxo de trabalho para usuários operacionais;
- ✅ Entrada rápida para os módulos críticos do sistema;
- ✅ Organização visual focada em produtividade;

## 🔐 Controle de Acesso:

- Todos os usuários autenticados têm acesso
- Cards específicos (como Auditoria) aparecem apenas para Admins

## 📱 Responsividade:

- Desktop: Grid de 3-4 colunas;
- Tablet: Grid de 2 colunas;
- Mobile: 1 coluna com scroll vertical;