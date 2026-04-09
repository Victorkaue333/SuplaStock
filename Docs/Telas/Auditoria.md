# 👨‍💼 Tela: Auditoria (Gestão de Usuários)

## 📍 Localização:

**URL:** `/auth/auditoria/`
**View:** `usuarios.views.auditoria_view`
**Template:** `usuarios/auditoria.html`
**Permissão:** Apenas Admin

## 🎯 Objetivo:

Permitir que administradores gerenciem usuários do sistema, incluindo criação, edição, exclusão e controle de permissões.

## ⚙️ Funcionalidades Principais

### Listagem de Usuários:

Tabela com:

- ID;
- Nome;
- Email;
- Papel (Admin/Operação);
- Status (Ativo/Inativo);
- Data de Cadastro;
- Último Acesso;
- Total de Acessos;
- Ações (Editar/Resetar Senha/Deletar);

### Criar Usuário:

Formulário:

- **Nome*** - Máx 150 caracteres;
- **Email*** - Email válido único;
- **Papel*** - Select (Admin/Operação);
- **Senha Inicial*** - Mínimo 8 caracteres;
- **Confirmar Senha*** - Deve ser idêntica;
- **Status** - Ativo/Inativo (padrão: Ativo);

### Editar Usuário:

Campos editáveis:

- Nome;
- Email;
- Papel;
- Status;

**Não permite:**

- Editar próprio papel (evita remoção de último admin);
- Desativar última conta admin;

### Resetar Senha de Usuário;

- Admin define nova senha temporária;
- Usuário deve trocar no primeiro login;
- Email enviado com nova senha;

### Deletar Usuário:

- Confirmação obrigatória;
- Não permite deletar:
  - Própria conta;
  - Última conta admin;
  - Usuários com vendas ativas;
- Registra log de exclusão;

### Histórico de Ações:

Tabela de auditoria:

- Data/Hora;
- Usuário Admin;
- Ação (Criou/Editou/Deletou/Resetou);
- Usuário Afetado;
- Detalhes;

## 🔄 Fluxo de Navegação:

```
Home → Auditoria (Admin apenas)
   ├─→ Criar Usuário
   │    ├─→ Preencher formulário
   │    └─→ Salvar (envia email de boas-vindas)
   │
   ├─→ Editar Usuário
   │    ├─→ Modificar dados
   │    └─→ Atualizar
   │
   ├─→ Resetar Senha
   │    ├─→ Confirmar ação
   │    └─→ Nova senha gerada e enviada
   │
   └─→ Deletar Usuário
        ├─→ Confirmar exclusão
        └─→ Removido permanentemente
```

## 📋 Validações:

- ✅ Email único no sistema;
- ✅ Não pode remover último admin;
- ✅ Não pode editar próprio papel;
- ✅ Senha inicial forte (8+ caracteres);
- ✅ Nome não pode ser vazio;

## 🎨 Layout:

- Tabela responsiva;
- Badge de papel (Admin=vermelho, Operação=azul);
- Badge de status (Ativo=verde, Inativo=cinza);
- Modal para criar/editar;
- Confirmação com SweetAlert para ações críticas;

## 🔐 Segurança:

- Acesso exclusivo para Admin;
- Log completo de todas as ações;
- Proteção contra remoção acidental de admins;
- Senhas sempre criptografadas;

## 📱 Responsividade:

- Desktop: Tabela completa;
- Mobile: Cards com informações essenciais;

## 🔗 Integrações:

- **Perfil:** Usuários podem ver próprio perfil;
- **Login:** Controla acesso ao sistema;
- **Logs:** Registra todas as ações administrativas;
