# SuplaStock - Guia de ProduÃ§Ã£o

AnÃ¡lise tÃ©cnica deste repositÃ³rio em `21/03/2026`.

## 1. ðŸ“‹ VisÃ£o Geral do Projeto:

Sistema web para operaÃ§Ã£o de loja de suplementos com mÃ³dulos de:

- autenticaÃ§Ã£o e controle de acesso (`usuarios`)
- estoque (`estoque`)
- vendas (`vendas`)
- financeiro (`financeiro`)

### Stack atual:

- Python 3 + Django 5.1
- SQLite (atual no projeto), com suporte em cÃ³digo para PostgreSQL
- WhiteNoise para estÃ¡ticos
- Nginx como reverse proxy
- Scripts de operaÃ§Ã£o e backup

## 2. âš ï¸ Status Atual do Projeto:

### O que jÃ¡ estÃ¡ pronto para produÃ§Ã£o

- Estrutura modular de apps organizada.
- MigraÃ§Ãµes existentes para `usuarios`, `estoque`, `vendas` e `financeiro`.
- `settings.py` com variÃ¡veis de ambiente (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, banco, cache, email).
- `STATIC_ROOT`, `MEDIA_ROOT`, WhiteNoise e endpoint de health check (`/health/`).
- Templates de Nginx e script de backup PostgreSQL (`scripts/backup.sh`).

### O que estÃ¡ incompleto ou ausente:

- `settings_prod.py` estÃ¡ inconsistente com o estado atual do projeto (referÃªncia a `gestao.Usuario` e middlewares/apps nÃ£o presentes). Hoje ele quebra na inicializaÃ§Ã£o.
- `requirements.txt` nÃ£o inclui dependÃªncias obrigatÃ³rias de produÃ§Ã£o para este cenÃ¡rio: `gunicorn` e `psycopg2-binary`.
- Scripts de deploy (`scripts/deploy.sh` e `scripts/deploy.bat`) dependem de `docker-compose`, mas nÃ£o hÃ¡ `docker-compose*.yml` nem `Dockerfile` no repositÃ³rio.
- Testes automatizados dos apps estÃ£o vazios (arquivos `tests.py` padrÃ£o do Django).
- Pipeline `.github/workflows/ci.yml` ainda referencia app `gestao` e build Docker, desalinhado com a estrutura atual.
- EstratÃ©gia de `.env` estÃ¡ inconsistente entre scripts (`suplastock/config/.env`) e execuÃ§Ã£o do Django (que lÃª variÃ¡veis do ambiente do processo).

## 3. ðŸš¨ Checklist de ProduÃ§Ã£o (CRÃTICO):

Marque tudo antes do go-live:

- [ ] Definir padrÃ£o Ãºnico de variÃ¡veis de ambiente e carregar no processo do Gunicorn (`EnvironmentFile` no systemd).
- [ ] Configurar `SECRET_KEY` forte (Ãºnica, 50+ caracteres, nunca versionada).
- [ ] Configurar `DEBUG=False`.
- [ ] Configurar `ALLOWED_HOSTS` com domÃ­nio real.
- [ ] Configurar `CSRF_TRUSTED_ORIGINS` com URLs HTTPS reais.
- [ ] Migrar banco de `SQLite` para `PostgreSQL`.
- [ ] Adicionar `psycopg2-binary` no ambiente/requirements.
- [ ] Adicionar `gunicorn` no ambiente/requirements.
- [ ] Configurar `STATIC_ROOT`/`MEDIA_ROOT` e permissÃµes no servidor.
- [ ] Rodar `python manage.py collectstatic --noinput`.
- [ ] Configurar serviÃ§o `systemd` para Gunicorn.
- [ ] Configurar Nginx com proxy para Gunicorn e aliases de `/static/` e `/media/`.
- [ ] Habilitar HTTPS (Certbot) e manter `SECURE_SSL=True`.
- [ ] Validar cookies seguros e proteÃ§Ãµes CSRF (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS).
- [ ] Rodar migraÃ§Ãµes em produÃ§Ã£o (`python manage.py migrate --noinput`).
- [ ] Criar superusuÃ¡rio (`python manage.py createsuperuser`).
- [ ] Executar scripts iniciais (`adicionar_categorias.py`, `gerar_codigos_clientes.py`).
- [ ] Corrigir `settings_prod.py` ou padronizar produÃ§Ã£o usando `suplastock.settings` atÃ© a correÃ§Ã£o.

## 4. âš™ï¸ ConfiguraÃ§Ã£o de ProduÃ§Ã£o (Passo a Passo - Ubuntu):

### 4.1 Preparar servidor:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib
```

### 4.2 Clonar projeto e criar venv:

```bash
sudo mkdir -p /opt/va-suplementos
sudo chown -R $USER:$USER /opt/va-suplementos
cd /opt/va-suplementos
git clone <URL_DO_REPOSITORIO> app
cd app

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Enquanto requirements.txt nÃ£o for atualizado:
pip install gunicorn psycopg2-binary
```

### 4.3 Configurar PostgreSQL:

```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE suplastock_prod;
CREATE USER suplastock_user WITH PASSWORD 'troque-esta-senha';
GRANT ALL PRIVILEGES ON DATABASE suplastock_prod TO suplastock_user;
SQL
```

### 4.4 Configurar variÃ¡veis de ambiente:

```bash
sudo tee /etc/va-suplementos.env > /dev/null <<'EOF'
DJANGO_SETTINGS_MODULE=suplastock.settings
DJANGO_ENV=production
SECRET_KEY=troque-por-uma-chave-forte
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

DATABASE_ENGINE=postgresql
DATABASE_NAME=suplastock_prod
DATABASE_USER=suplastock_user
DATABASE_PASSWORD=troque-esta-senha
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

SECURE_SSL=True
CACHE_BACKEND=dummy
EMAIL_BACKEND=console
DEFAULT_FROM_EMAIL=noreply@seu-dominio.com
STORAGE_BACKEND=local
EOF

sudo chmod 600 /etc/va-suplementos.env
```

### 4.5 Migrar banco, coletar estÃ¡ticos e preparar dados iniciais:

```bash
cd /opt/va-suplementos/app/suplastock
source /opt/va-suplementos/app/venv/bin/activate
set -a
source /etc/va-suplementos.env
set +a

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py createsuperuser
python scripts/adicionar_categorias.py
python scripts/gerar_codigos_clientes.py
python manage.py check --deploy
```

### 4.6 Configurar Gunicorn (systemd):

```bash
sudo chown -R www-data:www-data /opt/va-suplementos/app
```

```bash
sudo tee /etc/systemd/system/va-suplementos.service > /dev/null <<'EOF'
[Unit]
Description=SuplaStock Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/va-suplementos/app/suplastock
EnvironmentFile=/etc/va-suplementos.env
ExecStart=/opt/va-suplementos/app/venv/bin/gunicorn --workers 3 --timeout 120 --bind unix:/run/va-suplementos.sock suplastock.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now va-suplementos
sudo systemctl status va-suplementos --no-pager
```

### 4.7 Configurar Nginx:

```bash
sudo tee /etc/nginx/sites-available/va-suplementos > /dev/null <<'EOF'
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    client_max_body_size 20M;

    location /static/ {
        alias /opt/va-suplementos/app/suplastock/staticfiles/;
        expires 30d;
        access_log off;
    }

    location /media/ {
        alias /opt/va-suplementos/app/suplastock/media/;
        expires 7d;
        access_log off;
    }

    location /health/ {
        include proxy_params;
        proxy_pass http://unix:/run/va-suplementos.sock;
        access_log off;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/va-suplementos.sock;
    }
}
EOF
```

```bash
sudo ln -sf /etc/nginx/sites-available/va-suplementos /etc/nginx/sites-enabled/va-suplementos
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### 4.8 Habilitar HTTPS (recomendado antes do go-live):

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
sudo systemctl reload nginx
```

## 5. ðŸ” VariÃ¡veis de Ambiente (`.env.example`):

Arquivo de referÃªncia para produÃ§Ã£o (`/etc/va-suplementos.env` ou equivalente):

```env
# Django
DJANGO_SETTINGS_MODULE=suplastock.settings
DJANGO_ENV=production
SECRET_KEY=troque-por-uma-chave-forte-com-50+-caracteres
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
SECURE_SSL=True

# Database
DATABASE_ENGINE=postgresql
DATABASE_NAME=suplastock_prod
DATABASE_USER=suplastock_user
DATABASE_PASSWORD=troque-esta-senha
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432

# Cache
CACHE_BACKEND=dummy
# CACHE_BACKEND=redis
# REDIS_URL=redis://127.0.0.1:6379/0

# Email
EMAIL_BACKEND=console
# EMAIL_BACKEND=smtp
# EMAIL_HOST=smtp.seu-provedor.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=usuario
# EMAIL_HOST_PASSWORD=senha
DEFAULT_FROM_EMAIL=noreply@seu-dominio.com

# CORS (se necessÃ¡rio)
CORS_ALLOWED_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com

# Storage
STORAGE_BACKEND=local
# STORAGE_BACKEND=s3
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=
# AWS_S3_REGION_NAME=sa-east-1

# Observabilidade
SENTRY_DSN=
ADMIN_EMAIL=admin@seu-dominio.com
```

## 6. ðŸš€ Comandos de Deploy (copiar e colar):

### Setup inicial do servidor:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git nginx postgresql postgresql-contrib
```

### InstalaÃ§Ã£o da aplicaÃ§Ã£o e dependÃªncias:

```bash
sudo mkdir -p /opt/va-suplementos
sudo chown -R $USER:$USER /opt/va-suplementos
cd /opt/va-suplementos
git clone <URL_DO_REPOSITORIO> app
cd app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Executar projeto (bootstrap):

```bash
cd /opt/va-suplementos/app/suplastock
set -a && source /etc/va-suplementos.env && set +a
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py createsuperuser
python scripts/adicionar_categorias.py
python scripts/gerar_codigos_clientes.py
python manage.py check --deploy
```

### Subir Gunicorn:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now va-suplementos
sudo systemctl restart va-suplementos
sudo systemctl status va-suplementos --no-pager
```

## 7. ðŸš† Deploy na Railway (recomendado para este repositÃ³rio):

### 7.1 Ajustes necessÃ¡rios no cÃ³digo (jÃ¡ versionados):

- `railway.toml` na raiz com `buildCommand`, `preDeployCommand` e `startCommand` explÃ­citos para Django dentro de `suplastock/`.
- `requirements.txt` com dependÃªncias de produÃ§Ã£o: `gunicorn`, `psycopg2-binary`, `dj-database-url`.
- `suplastock/settings.py` aceitando `DATABASE_URL` (padrÃ£o Railway).

### 7.2 Configurar serviÃ§o na Railway:

1. Conecte o repositÃ³rio normalmente.
2. Em **Settings > Root Directory**, mantenha raiz do repositÃ³rio (`/`) para usar o `railway.toml`.
3. NÃ£o defina manualmente `Build Command`/`Start Command` (o arquivo `railway.toml` jÃ¡ define).
4. Adicione um serviÃ§o PostgreSQL no mesmo projeto da Railway.

### 7.3 VariÃ¡veis de ambiente mÃ­nimas:

- `SECRET_KEY=<chave forte>`
- `DEBUG=False`
- `ALLOWED_HOSTS=<seu-servico>.up.railway.app`
- `CSRF_TRUSTED_ORIGINS=https://<seu-servico>.up.railway.app`
- `SECURE_SSL=True`
- `DATABASE_URL=${{Postgres.DATABASE_URL}}` (ou valor direto da variÃ¡vel criada pelo plugin Postgres)

### 7.4 Erro "No start command detected":

Se esse erro reaparecer, confirme se o deploy estÃ¡ usando o commit que contÃ©m `railway.toml`. Sem esse arquivo, o Railpack tenta inferir o start automaticamente e pode falhar quando o `manage.py` estÃ¡ em subdiretÃ³rio.

## 8. ðŸ§ª Testes Antes de Ir para ProduÃ§Ã£o:

### Testes tÃ©cnicos:

- `python manage.py check --deploy`
- `python manage.py migrate --plan`
- `python manage.py test`
- `curl -I http://127.0.0.1/health/` (ou domÃ­nio final)

### Testes funcionais obrigatÃ³rios:

- Login: autenticar com usuÃ¡rio admin e usuÃ¡rio comum, validar logout e bloqueio de rotas privadas.
- Estoque: cadastrar produto, editar, baixar estoque por venda e validar listagens/relatÃ³rios.
- Vendas: registrar venda com mÃºltiplos itens e formas de pagamento, validar atualizaÃ§Ã£o de estoque.
- Financeiro: criar conta a pagar e conta a receber, lanÃ§ar pagamento e validar dashboard.
- IntegraÃ§Ã£o entre mÃ³dulos: venda fiada deve criar conta a receber; recebimento deve refletir no financeiro; cancelamento deve reverter estoque e estado financeiro quando aplicÃ¡vel.

## 9. ðŸ“¦ Melhorias Futuras (opcional):

- Docker: adicionar `Dockerfile` + `docker-compose` reais para ambiente local/staging/prod.
- CI/CD: corrigir workflow atual para apps modulares (`usuarios`, `estoque`, `vendas`, `financeiro`) e remover referÃªncias legadas a `gestao`.
- Monitoramento: Sentry em produÃ§Ã£o, mÃ©tricas de infraestrutura e alertas de disponibilidade.
- Observabilidade: centralizaÃ§Ã£o de logs (Loki/ELK) e dashboard de healthchecks.

