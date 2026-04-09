import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplastock.settings')
django.setup()

from estoque.models import Categoria

def adicionar_categorias():
    """Adiciona categorias de produtos de academia"""
    
    categorias = [
        'Whey Protein',
        'TermogÃªnico',
        'PrÃ©-Treino',
        'Creatina',
        'BCAA',
        'HipercalÃ³rico',
        'Barras de ProteÃ­na',
        'Vitaminas',
        'Glutamina',
        'Ã”mega 3',
    ]
    
    print("\n" + "="*50)
    print("ADICIONANDO CATEGORIAS DE PRODUTOS")
    print("="*50 + "\n")
    
    for nome_cat in categorias:
        categoria, criada = Categoria.objects.get_or_create(nome=nome_cat)
        
        if criada:
            print(f"âœ… Categoria '{categoria.nome}' criada com sucesso!")
        else:
            print(f"â„¹ï¸  Categoria '{categoria.nome}' jÃ¡ existe")
    
    print("\n" + "="*50)
    print("CATEGORIAS CADASTRADAS NO SISTEMA")
    print("="*50 + "\n")
    
    todas_categorias = Categoria.objects.all()
    for idx, cat in enumerate(todas_categorias, 1):
        print(f"{idx}. {cat.nome}")
    
    print("\n" + "="*50)
    print(f"Total: {todas_categorias.count()} categorias")
    print("="*50 + "\n")

if __name__ == '__main__':
    adicionar_categorias()

