# 👤 Tela: Perfil

## 📍 Localização:

**URL:** `/auth/perfil/`
**View:** `usuarios.views.perfil_view`
**Template:** `usuarios/perfil.html`
**Permissão:** Usuários autenticados

## 🎯 Objetivo:

Visualizar e editar informações pessoais do usuário logado, incluindo histórico de acessos e alteração de senha.

## ⚙️ Funcionalidades Principais:

### Informações do Perfil:

Exibidas:

- Nome completo;
- Email;
- Papel (Admin/Operação);
- Data de cadastro;
- Último acesso;
- Total de acessos;

### Edição de Dados:

Campos editáveis:

- **Nome*** - Texto, máx 150 caracteres;
- **Email*** - Email válido único;

Botão: **Salvar Alterações**

### Alterar Senha:

Link para página dedicada:

- Senha atual;
- Nova senha;
- Confirmar nova senha;

### Histórico de Acessos:

Tabela com últimos 20 acessos:

- Data e hora;
- IP de origem;
- Navegador/Dispositivo;
- Status (Sucesso/Falha);

## 🔄 Fluxo de Navegação

```
Home → Perfil
   ├─→ Editar Dados → Salvar
   ├─→ Alterar Senha → Formulário → Confirmar
   └─→ Ver Histórico de Acessos
```

## 🎨 Layout:

- Card com informações do usuário;
- Avatar (iniciais do nome);
- Formulário de edição;
- Tabela de histórico;
- Badges para papel do usuário;

## 🔐 Segurança:

- Usuário só pode editar próprio perfil;
- Alteração de senha requer senha atual;
- Log de todas as alterações;