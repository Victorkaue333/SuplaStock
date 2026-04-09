<div align="center">

# 💊 SuplaStock:

## Sistema Web para Gestão Completa de Loja de Suplementos:

Sistema web robusto desenvolvido para gestão de loja de suplementos, integrando estoque, vendas, clientes e financeiro em uma única aplicação Django. O sistema oferece funcionalidades avançadas como controle de estoque, emissão de notas fiscais, dashboards operacionais e financeiros, além de relatórios detalhados em PDF e Excel. Com uma interface intuitiva e responsiva, o SuplaStock é a solução ideal para otimizar a gestão e impulsionar o crescimento do seu negócio;

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet?logo=railway&logoColor=white)](https://railway.app/)

</div>

---

## 📋 Sobre o Projeto:

Solução completa de gestão com foco em eficiência operacional e facilidade de uso, integrando todas as áreas críticas do negócio em uma única plataforma.

## 🚀 Módulos e Funcionalidades:

Abaixo estão listados os principais módulos e funcionalidades do sistema, detalhando as capacidades de cada área:

### 👤 Usuários e Autenticação:

- 🔐 Login, logout e controle de sessão;
- 🔑 Recuperação e redefinição de senha por token;
- 📝 Perfil do usuário com histórico de acessos;
- 👥 Níveis de acesso por papel (admin e operação);

### 📦 Estoque:

O módulo de estoque é projetado para oferecer controle total sobre os produtos, desde o cadastro até a gestão de inventário. As funcionalidades incluem:

- ➕ Cadastro, edição e exclusão de produtos;
- 🏷️ Categoria, fornecedor, custo, preço sugerido e margem automática;
- ⚠️ Controle de estoque mínimo, validade e produtos zerados;
- 📊 Relatório de estoque com alertas;

### 🛒 Vendas e Clientes:

Area de vendas é o coração do sistema, oferecendo uma experiência completa para o processo de venda, desde a seleção de produtos até a finalização do pagamento e emissão de nota fiscal. As funcionalidades incluem:

- 🛍️ Registro de vendas com carrinho de múltiplos itens;
- 📦 Agrupamento por transação;
- 👥 Gestão de clientes e tela de cobrança;
- 💰 Pagamentos parciais e atualização automática de status;
- 🧾 Emissão de nota fiscal simplificada em PDF;

### 💵 Financeiro;.

- 📈 Dashboard operacional e dashboard financeiro;
- 💸 Fluxo de caixa (entradas × saídas);
- 🧾 Contas a receber (avulsa e fiado) com filtros e alertas;
- ✅ Recebimento, cancelamento, edição e detalhe de contas;
- 🔌 APIs internas para busca de produtos/clientes;

### 📑 Relatórios e Exportações:

- 📄 Vendas em PDF e Excel;
- 📦 Estoque em PDF;
- 🏆 Ranking de clientes em Excel;
- 💰 Contas a receber em PDF e Excel;

---

## 📦 Stack Técnica Detalhada:

O projeto utiliza uma combinação de tecnologias modernas e robustas para garantir desempenho, segurança e escalabilidade. Abaixo está a stack técnica detalhada:

```text
Backend:
├── Python 3.11
├── Django 5.1
├── Django REST Framework
├── WhiteNoise (static files)
├── django-health-check
└── django-cors-headers

Database:
├── SQLite (desenvolvimento)
└── PostgreSQL (produção)

Frontend:
├── HTML5
├── CSS3
├── JavaScript (ES6+)
└── Bootstrap 5

Exports:
├── ReportLab (PDF)
└── openpyxl (Excel)

Deploy:
├── Railway (PaaS)
├── Gunicorn (WSGI)
└── Nginx (Reverse Proxy)
```

---

## 📁 Estrutura do Projeto:

A estrutura do projeto é organizada para facilitar a manutenção e escalabilidade, com separação clara entre módulos, configurações e documentação. Abaixo está um resumo da estrutura de diretórios e arquivos:

```text
SuplaStock/
├── railway.toml                    # Configuração de deploy Railway
├── README.md                       # Documentação principal
├── requirements.txt                # Dependências Python
├── runtime.txt                     # Versão Python para deploy
│
├── Doc/                            # Documentação técnica e funcional
│   ├── guia_producao.md
│   ├── melhorias_arquitetura.md
│   ├── site_institucional_proposta.md
│   ├── auditoria/                  # Auditorias e roadmap
│   ├── fluxos/                     # Fluxos de negócio
│   ├── Funcionalidades/            # Documentação de features
│   ├── ideias/                     # Propostas e melhorias
│   └── Telas/                      # Documentação de interfaces
│
├── nginx/                          # Configurações Nginx
│   ├── nginx.conf
│   ├── conf.d/
│   └── ssl/
│
├── scripts/                        # Scripts de deploy e backup
│   ├── backup.sh
│   ├── deploy.bat
│   └── deploy.sh
│
└── suplastock/                 # Aplicação Django principal
    ├── manage.py
    │
    ├── config/                     # Configurações e paths
    │   ├── __init__.py
    │   ├── paths.py
    │   └── pytest.ini
    │
    ├── data/                       # Banco de dados SQLite local
    │   ├── db.sqlite3
    │   └── db.sqlite3.backup
    │
    ├── usuarios/                   # Autenticação e perfis
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── decorators.py
    │   ├── middleware.py
    │   ├── templates/
    │   └── migrations/
    │
    ├── estoque/                    # Gestão de produtos e estoque
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── templates/
    │   ├── management/
    │   └── migrations/
    │
    ├── vendas/                     # Vendas e clientes
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── templates/
    │   └── migrations/
    │
    ├── financeiro/                 # Financeiro e dashboards
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── templates/
    │   ├── templatetags/
    │   └── migrations/
    │
    ├── gestao/                     # Gestão e utilidades
    │   ├── utils/
    │   └── migrations/
    │
    ├── va_suplementos/             # Settings e configurações Django
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── settings_prod.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   ├── asgi.py
    │   ├── context_processors.py
    │   ├── templates/              # Templates base
    │   └── utils/
    │
    ├── static/                     # Arquivos estáticos
    │   ├── css/
    │   ├── js/
    │   ├── img/
    │   └── media/
    │
    ├── staticfiles/                # Arquivos coletados (deploy)
    ├── scripts/                    # Management commands
    ├── tests/                      # Testes
    ├── logs/                       # Logs da aplicação
    ├── media/                      # Uploads de usuários
    └── backups/                    # Backups do sistema
```

---

## 🚀 Como Rodar Localmente?:

### 📋 Pré-requisitos:

Para rodar esse projeto é necessário:

- Python 3.11 ou superior;
- pip (gerenciador de pacotes Python);
- Git;

### 🔧 Instalação:

**1. Clone o repositório:**

```bash
git clone
cd
```

**2. Crie e ative um ambiente virtual:**

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Instale as dependências:**

```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente:**

**Windows:**

```bash
copy
```

**Linux/macOS:**

```bash
cp
```

**5. Execute as migrações e cargas iniciais:**

```bash
cd SuplaStock
python manage.py migrate
python manage.py ensure_default_categories
```

**6. (Opcional) Crie o usuário admin:**

**Windows:**

```bash
set BOOTSTRAP_ADMIN_USERNAME=admin
set BOOTSTRAP_ADMIN_EMAIL=admin@local.test
set BOOTSTRAP_ADMIN_PASSWORD=SenhaForte123!
python manage.py ensure_bootstrap_admin
```

**Linux/macOS:**

```bash
export BOOTSTRAP_ADMIN_USERNAME=admin
export BOOTSTRAP_ADMIN_EMAIL=admin@local.test
export BOOTSTRAP_ADMIN_PASSWORD=SenhaForte123!
python manage.py ensure_bootstrap_admin
```

**7. Inicie o servidor de desenvolvimento:**

```bash
python manage.py runserver
```

✅ **Aplicação rodando em:** http://127.0.0.1:8000/

---

## 👨‍💻 Autor:

<div align="center">

**Victor Alves**

[![GitHub](https://img.shields.io/badge/GitHub-Victorkaue333-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Victorkaue333)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Victor_Alves-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/victor-alves)

---
</div>