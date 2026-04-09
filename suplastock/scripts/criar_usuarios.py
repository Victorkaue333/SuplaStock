# Script para criar usuÃ¡rios iniciais do sistema
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suplastock.settings')
django.setup()

from usuarios.models import Usuario

# Criar superusuÃ¡rio admin
if not Usuario.objects.filter(username='admin').exists():
    admin = Usuario.objects.create_superuser(
        username='admin',
        email='admin@vasuplementos.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        nivel_acesso='admin'
    )
    print('âœ… SuperusuÃ¡rio ADMIN criado com sucesso!')
else:
    print('âš ï¸  UsuÃ¡rio admin jÃ¡ existe')

# Criar vendedor de teste
if not Usuario.objects.filter(username='vendedor').exists():
    vendedor = Usuario.objects.create_user(
        username='vendedor',
        email='vendedor@vasuplementos.com',
        password='vendedor123',
        first_name='JoÃ£o',
        last_name='Vendedor',
        nivel_acesso='vendedor'
    )
    print('âœ… UsuÃ¡rio VENDEDOR criado com sucesso!')
else:
    print('âš ï¸  UsuÃ¡rio vendedor jÃ¡ existe')

# Criar estoquista de teste
if not Usuario.objects.filter(username='estoquista').exists():
    estoquista = Usuario.objects.create_user(
        username='estoquista',
        email='estoquista@vasuplementos.com',
        password='estoquista123',
        first_name='Maria',
        last_name='Estoquista',
        nivel_acesso='estoquista'
    )
    print('âœ… UsuÃ¡rio ESTOQUISTA criado com sucesso!')
else:
    print('âš ï¸  UsuÃ¡rio estoquista jÃ¡ existe')

print('\n' + '='*50)
print('USUÃRIOS CRIADOS - Credenciais:')
print('='*50)
print('ADMIN:')
print('  Username: admin')
print('  Password: admin123')
print('  NÃ­vel: Administrador')
print('')
print('VENDEDOR:')
print('  Username: vendedor')
print('  Password: vendedor123')
print('  NÃ­vel: Vendedor')
print('')
print('ESTOQUISTA:')
print('  Username: estoquista')
print('  Password: estoquista123')
print('  NÃ­vel: Estoquista')
print('='*50)

