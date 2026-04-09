# ðŸ” Tela: Login

## ðŸ“ LocalizaÃ§Ã£o:

**URL:** `/` ou `/login/`
**View:** `usuarios.views.login_view`
**Template:** `usuarios/login.html`
**PermissÃ£o:** Acesso pÃºblico

## ðŸŽ¯ Objetivo:

Tela de autenticaÃ§Ã£o que controla o acesso ao sistema, validando credenciais e iniciando sessÃ£o do usuÃ¡rio.

## âš™ï¸ Funcionalidades Principais:

### FormulÃ¡rio de Login:

Campos:

- **Email*** - Email cadastrado do usuÃ¡rio;
- **Senha*** - Senha de acesso;
- **Lembrar-me** - Checkbox para manter sessÃ£o ativa;

BotÃµes:

- **Entrar** - Submete credenciais;
- **Esqueci minha senha** - Link para recuperaÃ§Ã£o;

### ValidaÃ§Ãµes:

- âœ… Email deve ser vÃ¡lido;
- âœ… Senha Ã© obrigatÃ³ria;
- âŒ Bloqueia apÃ³s 5 tentativas falhas (15 min);
- âœ… Verifica se usuÃ¡rio estÃ¡ ativo;
- âœ… Registra log de acesso;

### RecuperaÃ§Ã£o de Senha:

- Link direto para tela de recuperaÃ§Ã£o;
- Sistema de token por email;

## ðŸ”„ Fluxo de NavegaÃ§Ã£o:

```
Login
   â”œâ”€â†’ Credenciais corretas â†’ Home
   â”œâ”€â†’ Credenciais incorretas â†’ Mensagem de erro
   â”œâ”€â†’ Esqueci minha senha â†’ Recuperar Senha
   â””â”€â†’ Conta bloqueada â†’ Mensagem de bloqueio
```

## ðŸŽ¨ Layout:

- Design centralizado;
- Logo do SuplaStock;
- FormulÃ¡rio limpo e responsivo;
- Feedback visual de erros;
- Loading spinner ao submeter;

## ðŸ” SeguranÃ§a:

- Senha criptografada (bcrypt);
- ProteÃ§Ã£o CSRF;
- Rate limiting anti-brute force;
- Logs de tentativas de acesso;

## ðŸ“± Responsividade:

- Funciona em desktop, tablet e mobile;
- Layout adaptado para cada tela;
