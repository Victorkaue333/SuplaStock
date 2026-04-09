"""
Scripts UtilitÃ¡rios - SuplaStock
=====================================

Scripts de administraÃ§Ã£o e utilitÃ¡rios para o sistema SuplaStock.

Scripts disponÃ­veis:
- adicionar_categorias.py: Adiciona categorias de produtos
- criar_usuarios.py: Cria usuÃ¡rios do sistema  
- gerar_codigos_clientes.py: Gera cÃ³digos Ãºnicos para clientes
- remover_usuarios.py: Remove usuÃ¡rios do sistema

Uso:
    python scripts/nome_do_script.py

Nota: Execute sempre a partir do diretÃ³rio raiz do projeto Django.
"""

import os
import sys
import django

# Adiciona o diretÃ³rio pai ao path para importar o Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplastock.settings')
django.setup()
