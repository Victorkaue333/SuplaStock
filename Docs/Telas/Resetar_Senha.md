# 🔐 Tela: Resetar Senha

## 📍 Localização:

**URL:** `/auth/resetar-senha/<token>/`
**View:** `usuarios.views.resetar_senha_view`
**Template:** `usuarios/resetar_senha.html`
**Permissão:** Acesso público com token válido

## 🎯 Objetivo:

Permitir que o usuário defina uma nova senha após solicitar recuperação.

## ⚙️ Funcionalidades Principais

### Formulário:

Campos:

- **Nova Senha*** - Mínimo 8 caracteres;
- **Confirmar Senha*** - Deve ser idêntica;

Botão:~

- **Redefinir Senha**

### Validações:

- ✅ Token deve ser válido;
- ✅ Token não pode estar expirado;
- ✅ Senha mínimo 8 caracteres;
- ✅ Senha deve ter letra e número;
- ✅ Senhas devem ser idênticas;
- ✅ Nova senha não pode ser igual à anterior;

### Processo:

1. Usuário acessa link com token;
2. Sistema valida token;
3. Se válido: Exibe formulário;
4. Se inválido: Mensagem de erro;
5. Usuário define nova senha;
6. Senha atualizada e token invalidado;
7. Redirecionamento automático para login;

## 🔄 Fluxo de Navegação:

```
Email → Link com Token → Resetar Senha
   ├─→ Token válido → Formulário
   │    ├─→ Definir nova senha
   │    └─→ Sucesso → Login
   │
   └─→ Token inválido → Erro
        └─→ Solicitar novo link
```

## 🎨 Layout:

- Design centralizado;
- Ícone de cadeado;
- Indicador visual de força da senha;
- Feedback em tempo real;
- Mensagem de sucesso;

## 🔐 Segurança:

- Token de uso único;
- Validade de 1 hora;
- Token invalidado após uso;
- Log de alteração de senha;
- Notificação por email da troca;
