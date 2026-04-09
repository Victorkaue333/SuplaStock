import os
import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


def _env_first(*keys):
    for key in keys:
        value = os.getenv(key, '').strip()
        if value:
            return value
    return ''


def _split_name(full_name):
    parts = (full_name or '').strip().split()
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], ' '.join(parts[1:])


def _resolve_username(default_username, email):
    if default_username:
        return default_username
    if '@' in (email or ''):
        return email.split('@', 1)[0].strip() or email
    return email or 'usuario'


def _generate_temp_password(length=14):
    alphabet = string.ascii_letters + string.digits + '!@#$%*-_'
    while True:
        candidate = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in candidate)
            and any(c.isupper() for c in candidate)
            and any(c.isdigit() for c in candidate)
        ):
            return candidate


def _find_user(user_model, *, email='', username='', full_name=''):
    if email:
        by_email = user_model.objects.filter(email__iexact=email).first()
        if by_email:
            return by_email

    if username:
        by_username = user_model.objects.filter(username=username).first()
        if by_username:
            return by_username

    first_name, last_name = _split_name(full_name)
    if first_name and last_name:
        by_name = user_model.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name,
        ).first()
        if by_name:
            return by_name

    return None


def _apply_profile(user, *, username, email, full_name, role, is_staff=True, is_superuser=False):
    first_name, last_name = _split_name(full_name)
    changed = False

    if user.username != username:
        user.username = username
        changed = True
    if (user.email or '').lower() != (email or '').lower():
        user.email = email
        changed = True
    if user.first_name != first_name:
        user.first_name = first_name
        changed = True
    if user.last_name != last_name:
        user.last_name = last_name
        changed = True
    if hasattr(user, 'nivel_acesso') and user.nivel_acesso != role:
        user.nivel_acesso = role
        changed = True
    if hasattr(user, 'ativo') and not user.ativo:
        user.ativo = True
        changed = True
    if not user.is_active:
        user.is_active = True
        changed = True
    if bool(user.is_staff) != bool(is_staff):
        user.is_staff = is_staff
        changed = True
    if bool(user.is_superuser) != bool(is_superuser):
        user.is_superuser = is_superuser
        changed = True

    if changed:
        user.save()
    return changed


class Command(BaseCommand):
    help = (
        'Garante os perfis principais do sistema: '
        'Administrador (cliente) e Desenvolvedor/Auditor.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-name',
            default=_env_first('ADMIN_CLIENT_NAME') or 'Vinicius Alves',
            help='Nome do administrador cliente.',
        )
        parser.add_argument(
            '--admin-email',
            default=_env_first('ADMIN_CLIENT_EMAIL'),
            help='Email do administrador cliente (opcional, ajuda na localizacao).',
        )
        parser.add_argument(
            '--admin-username',
            default=_env_first('ADMIN_CLIENT_USERNAME'),
            help='Username do administrador cliente (opcional, ajuda na localizacao).',
        )
        parser.add_argument(
            '--dev-name',
            default=_env_first('DEV_AUDITOR_NAME') or 'Victor Alves',
            help='Nome do desenvolvedor/auditor.',
        )
        parser.add_argument(
            '--dev-email',
            default=_env_first('DEV_AUDITOR_EMAIL') or 'kaue.alves.dev@gmail.com',
            help='Email do desenvolvedor/auditor.',
        )
        parser.add_argument(
            '--dev-username',
            default=_env_first('DEV_AUDITOR_USERNAME') or 'kaue.alves.dev',
            help='Username do desenvolvedor/auditor.',
        )
        parser.add_argument(
            '--dev-password',
            default=_env_first('DEV_AUDITOR_PASSWORD'),
            help='Senha inicial do desenvolvedor/auditor.',
        )

    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_name = (options.get('admin_name') or '').strip()
        admin_email = (options.get('admin_email') or '').strip().lower()
        admin_username = (options.get('admin_username') or '').strip()

        dev_name = (options.get('dev_name') or '').strip()
        dev_email = (options.get('dev_email') or '').strip().lower()
        dev_username = _resolve_username(
            (options.get('dev_username') or '').strip(),
            dev_email,
        )
        dev_password = options.get('dev_password') or ''

        with transaction.atomic():
            admin_user = _find_user(
                user_model,
                email=admin_email,
                username=admin_username,
                full_name=admin_name,
            )
            if admin_user:
                admin_username_effective = _resolve_username(admin_username, admin_user.email or admin_user.username)
                _apply_profile(
                    admin_user,
                    username=admin_username_effective,
                    email=admin_user.email or admin_email,
                    full_name=admin_name or (admin_user.get_full_name() or admin_user.username),
                    role='admin',
                    is_staff=True,
                    is_superuser=admin_user.is_superuser,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Administrador cliente confirmado: {admin_user.get_full_name() or admin_user.username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        'Administrador cliente nao localizado automaticamente. '
                        'Nenhum usuario existente foi alterado.'
                    )
                )

            dev_user = _find_user(
                user_model,
                email=dev_email,
                username=dev_username,
                full_name=dev_name,
            )
            dev_created = False
            if not dev_user:
                dev_user = user_model(
                    username=dev_username,
                    email=dev_email,
                )
                dev_created = True

            _apply_profile(
                dev_user,
                username=dev_username,
                email=dev_email,
                full_name=dev_name,
                role='developer',
                is_staff=True,
                is_superuser=dev_user.is_superuser,
            )

            generated_password = ''
            if dev_password:
                if not dev_user.check_password(dev_password):
                    dev_user.set_password(dev_password)
                    dev_user.save()
            elif dev_created:
                generated_password = _generate_temp_password()
                dev_user.set_password(generated_password)
                dev_user.save()

            if dev_created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuario desenvolvedor/auditor criado: {dev_email} (username={dev_username})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuario desenvolvedor/auditor atualizado: {dev_email} (username={dev_username})'
                    )
                )

            if generated_password:
                self.stdout.write(
                    self.style.WARNING(
                        'Senha temporaria gerada para o DEV/Auditor: '
                        f'{generated_password}'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        'Altere esta senha no primeiro acesso.'
                    )
                )
