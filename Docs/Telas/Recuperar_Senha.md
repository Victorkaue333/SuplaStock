# 🔑 Tela: Recuperar Senha

## 📍 Localização:

**URL:** `/auth/recuperar-senha/`
**View:** `usuarios.views.recuperar_senha_view`
**Template:** `usuarios/recuperar_senha.html`
**Permissão:** Acesso público

## 🎯 Objetivo:

Permitir que usuários solicitem recuperação de senha através de token enviado por email.

## ⚙️ Funcionalidades Principais:

### Formulário:

Campo:

- **Email*** - Email cadastrado no sistema;

Botão:

- **Enviar Link de Recuperação**

### Processo:

1. Usuário informa email;
2. Sistema valida se email existe;
3. Gera token único com validade de 1 hora;
4. Envia email com link de recuperação;
5. Exibe mensagem de confirmação;

### Validações:

- ✅ Email deve estar cadastrado;
- ✅ Email deve ser válido;
- ⏱️ Token expira em 1 hora;
- 🛡️ Rate limiting: máximo 3 solicitações/hora;

## 🔄 Fluxo de Navegação:

```
Login → Esqueci minha senha → Recuperar Senha
   ├─→ Informar Email
   ├─→ Email enviado (check inbox)
   ├─→ Clicar no link do email
   └─→ Resetar Senha (nova tela)
```

## 📧 Email Enviado:

Contém:

- Link com token único;
- Instruções claras;
- Aviso de validade (1 hora);
- Link para suporte se não solicitou;

## 🎨 Layout:

- Design centralizado;
- Ícone de cadeado;
- Campo de email destacado;
- Mensagem de sucesso após envio;
- Link para voltar ao login;

## 🔐 Segurança:

- Token único e temporário;
- Não revela se email existe (mesmo feedback);
- Rate limiting contra abuso;
- Log de todas as solicitações;
