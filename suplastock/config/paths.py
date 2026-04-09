"""
ConfiguraÃ§Ãµes de Caminhos - SuplaStock
==========================================

Centraliza todos os caminhos importantes do projeto.
"""

import os
from pathlib import Path

# DiretÃ³rio base do projeto Django
BASE_DIR = Path(__file__).resolve().parent.parent

# DiretÃ³rios organizados
SCRIPTS_DIR = BASE_DIR / 'scripts'
DATA_DIR = BASE_DIR / 'data'
CONFIG_DIR = BASE_DIR / 'config'
LOGS_DIR = BASE_DIR / 'logs'
DOCS_DIR = BASE_DIR / 'docs'
TESTS_DIR = BASE_DIR / 'tests'
MEDIA_DIR = BASE_DIR / 'media'
STATIC_DIR = BASE_DIR / 'static'
STATICFILES_DIR = BASE_DIR / 'staticfiles'

# Arquivos de configuraÃ§Ã£o
ENV_FILE = CONFIG_DIR / '.env'
ENV_EXAMPLE_FILE = CONFIG_DIR / '.env.example'
PYTEST_CONFIG = CONFIG_DIR / 'pytest.ini'

# Arquivos de banco de dados
DATABASE_FILE = DATA_DIR / 'db.sqlite3'
DATABASE_BACKUP = DATA_DIR / 'db.sqlite3.backup'

# Garantir que diretÃ³rios existam
REQUIRED_DIRS = [
    SCRIPTS_DIR, DATA_DIR, CONFIG_DIR, LOGS_DIR, 
    DOCS_DIR, TESTS_DIR, MEDIA_DIR, STATIC_DIR
]

for directory in REQUIRED_DIRS:
    directory.mkdir(exist_ok=True)
