import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _split_full_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _guess_name(username: str, email: str) -> str:
    source = (email or username or "administrador").strip()
    local_part = source.split("@", 1)[0]
    normalized = (
        local_part.replace(".", " ")
        .replace("_", " ")
        .replace("-", " ")
    )
    normalized = " ".join(part for part in normalized.split() if part)
    return (normalized.title() or "Administrador").strip()


class Command(BaseCommand):
    help = (
        "Cria ou atualiza um usuario administrador de bootstrap usando "
        "argumentos ou variaveis de ambiente."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--name",
            default=_first_env(
                "BOOTSTRAP_ADMIN_NAME",
                "ADMIN_NAME",
                "DJANGO_SUPERUSER_NAME",
                "SUPERUSER_NAME",
            ),
            help="Nome completo do administrador.",
        )
        parser.add_argument(
            "--email",
            default=_first_env(
                "BOOTSTRAP_ADMIN_EMAIL",
                "ADMIN_EMAIL",
                "DJANGO_SUPERUSER_EMAIL",
                "SUPERUSER_EMAIL",
            ),
            help="Email do administrador.",
        )
        parser.add_argument(
            "--password",
            default=_first_env(
                "BOOTSTRAP_ADMIN_PASSWORD",
                "ADMIN_PASSWORD",
                "DJANGO_SUPERUSER_PASSWORD",
                "SUPERUSER_PASSWORD",
            ),
            help="Senha do administrador.",
        )
        parser.add_argument(
            "--username",
            default=_first_env(
                "BOOTSTRAP_ADMIN_USERNAME",
                "ADMIN_USERNAME",
                "DJANGO_SUPERUSER_USERNAME",
                "SUPERUSER_USERNAME",
            ),
            help=(
                "Username do administrador (opcional). "
                "Se omitido, usa o email."
            ),
        )

    def handle(self, *args, **options):
        name = (options.get("name") or "").strip()
        email = (options.get("email") or "").strip().lower()
        password = options.get("password") or ""
        username = (options.get("username") or "").strip()

        if not email and "@" in username:
            email = username.lower()
        if not username and email:
            username = email
        if not name:
            name = _guess_name(username=username, email=email)

        missing = []
        if not username:
            missing.append("username/BOOTSTRAP_ADMIN_USERNAME")
        if not email:
            missing.append("email/BOOTSTRAP_ADMIN_EMAIL")
        if not password:
            missing.append("password/BOOTSTRAP_ADMIN_PASSWORD")

        if missing:
            message = (
                "Bootstrap admin faltando: "
                + ", ".join(missing)
                + " (aceita tambem ADMIN_* e DJANGO_SUPERUSER_*)."
            )

            running_on_railway = bool(
                os.getenv("RAILWAY_PROJECT_ID")
                or os.getenv("RAILWAY_SERVICE_ID")
                or os.getenv("RAILWAY_ENVIRONMENT_ID")
            )
            required_explicitly = _first_env("BOOTSTRAP_ADMIN_REQUIRED", "ADMIN_REQUIRED").lower() in {
                "1", "true", "yes", "on"
            }

            if running_on_railway or required_explicitly:
                raise CommandError(message)

            self.stdout.write(self.style.WARNING("Bootstrap admin ignorado: " + message))
            return

        first_name, last_name = _split_full_name(name)
        User = get_user_model()

        with transaction.atomic():
            user_by_email = User.objects.filter(email__iexact=email).first()
            user_by_username = User.objects.filter(username=username).first()

            if (
                user_by_email
                and user_by_username
                and user_by_email.pk != user_by_username.pk
            ):
                raise CommandError(
                    "Conflito: email e username pertencem a usuarios diferentes."
                )

            user = user_by_email or user_by_username
            created = user is None
            changed = False

            if created:
                user = User(username=username, email=email)
                changed = True

            if user.username != username:
                user.username = username
                changed = True
            if (user.email or "").lower() != email:
                user.email = email
                changed = True
            if user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if user.last_name != last_name:
                user.last_name = last_name
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if not user.is_staff:
                user.is_staff = True
                changed = True
            if not user.is_superuser:
                user.is_superuser = True
                changed = True

            if hasattr(user, "ativo") and not user.ativo:
                user.ativo = True
                changed = True
            if hasattr(user, "nivel_acesso") and user.nivel_acesso != "admin":
                user.nivel_acesso = "admin"
                changed = True

            if not user.check_password(password):
                user.set_password(password)
                changed = True

            if changed:
                user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario admin de bootstrap criado: {email} (username={username})"
                )
            )
        elif changed:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario admin de bootstrap atualizado: {email} (username={username})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario admin de bootstrap ja estava consistente: {email} (username={username})"
                )
            )
