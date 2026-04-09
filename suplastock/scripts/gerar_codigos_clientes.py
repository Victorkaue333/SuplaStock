import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplastock.settings')
django.setup()

from vendas.models import Cliente
import time

def gerar_codigos_clientes():
    """Gera cÃ³digos para clientes que nÃ£o possuem"""
    clientes_sem_codigo = Cliente.objects.filter(codigo__isnull=True) | Cliente.objects.filter(codigo='')
    
    total = clientes_sem_codigo.count()
    
    if total == 0:
        print("âœ… Todos os clientes jÃ¡ possuem cÃ³digo!")
        return
    
    print(f"ðŸ”„ Gerando cÃ³digos para {total} cliente(s)...\n")
    
    for i, cliente in enumerate(clientes_sem_codigo, 1):
        # Gerar cÃ³digo baseado no ID e timestamp
        timestamp = str(int(time.time()))[-6:]
        codigo = f"CLI{str(cliente.id).zfill(4)}{timestamp[-3:]}"
        
        cliente.codigo = codigo
        cliente.save()
        
        print(f"âœ… Cliente {i}/{total}: {cliente.nome} â†’ CÃ³digo: {codigo}")
    
    print(f"\nâœ… CÃ³digos gerados com sucesso para {total} cliente(s)!")

if __name__ == '__main__':
    gerar_codigos_clientes()

