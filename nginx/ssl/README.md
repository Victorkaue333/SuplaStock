# Diretório para certificados SSL
Este diretório deve conter:
- `cert.pem` - Certificado SSL
- `key.pem` - Chave privada

**IMPORTANTE:** Nunca faça commit de arquivos .pem!

## Gerando certificado autoassinado (apenas para testes):
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem
```

## Usando Let's Encrypt (produção):
```bash
certbot certonly --standalone -d seudominio.com
cp /etc/letsencrypt/live/seudominio.com/fullchain.pem cert.pem
cp /etc/letsencrypt/live/seudominio.com/privkey.pem key.pem
```
