# Script para remover usuÃ¡rios extras e deixar apenas o admin
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplastock.settings')
django.setup()

from usuarios.models import Usuario

# Remover vendedor
try:
    vendedor = Usuario.objects.get(username='vendedor')
    vendedor.delete()
    print('âœ… UsuÃ¡rio VENDEDOR removido')
except Usuario.DoesNotExist:
    print('âš ï¸  UsuÃ¡rio vendedor nÃ£o existe')

# Remover estoquista
try:
    estoquista = Usuario.objects.get(username='estoquista')
    estoquista.delete()
    print('âœ… UsuÃ¡rio ESTOQUISTA removido')
except Usuario.DoesNotExist:
    print('âš ï¸  UsuÃ¡rio estoquista nÃ£o existe')

# Verificar se admin existe
if Usuario.objects.filter(username='admin').exists():
    print('âœ… UsuÃ¡rio ADMIN mantido')
    admin = Usuario.objects.get(username='admin')
    print(f'   Username: {admin.username}')
    print(f'   Email: {admin.email}')
    print(f'   NÃ­vel: {admin.nivel_acesso}')
else:
    print('âŒ UsuÃ¡rio admin nÃ£o encontrado')

print('\n' + '='*50)
print('SISTEMA CONFIGURADO PARA USO INDIVIDUAL')
print('='*50)
print('Apenas 1 usuÃ¡rio mantido: ADMIN')
print('='*50)

