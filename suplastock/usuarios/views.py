from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Count, Max, Q
from datetime import timedelta
from math import ceil
from urllib.parse import urlparse
from pathlib import Path
from collections import deque
import secrets
import string
import logging

from .models import Usuario, HistoricoAcesso, TokenRecuperacaoSenha
from .decorators import developer_requerido

logger = logging.getLogger(__name__)

LOGIN_THROTTLE_ENABLED = bool(getattr(settings, 'LOGIN_THROTTLE_ENABLED', True))
LOGIN_THROTTLE_MAX_ATTEMPTS = max(1, int(getattr(settings, 'LOGIN_THROTTLE_MAX_ATTEMPTS', 5)))
LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP = max(1, int(getattr(settings, 'LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP', 20)))
LOGIN_THROTTLE_WINDOW_SECONDS = max(60, int(getattr(settings, 'LOGIN_THROTTLE_WINDOW_SECONDS', 900)))
LOGIN_THROTTLE_LOCKOUT_SECONDS = max(60, int(getattr(settings, 'LOGIN_THROTTLE_LOCKOUT_SECONDS', 900)))
DAILY_LOGIN_SESSION_KEY = 'auth_login_date'
AUDIT_HISTORY_LIMIT = max(20, int(getattr(settings, 'AUDIT_HISTORY_LIMIT', 120)))
AUDIT_SESSIONS_LIMIT = max(20, int(getattr(settings, 'AUDIT_SESSIONS_LIMIT', 120)))
AUDIT_LOG_TAIL_LINES = max(20, int(getattr(settings, 'AUDIT_LOG_TAIL_LINES', 80)))
PRIMARY_DEVELOPER_EMAIL = str(
    getattr(settings, 'PRIMARY_DEVELOPER_EMAIL', 'kaue.alves.dev@gmail.com')
).strip().lower()
PRIMARY_DEVELOPER_USERNAME = str(
    getattr(settings, 'PRIMARY_DEVELOPER_USERNAME', 'kaue.alves.dev')
).strip()
AUDITORIA_ROLE_CHOICES = [
    ('developer', 'Desenvolvedor / Auditor'),
    ('admin', 'Administrador'),
    ('vendedor', 'Vendedor'),
]


def get_client_ip(request):
    """ObtÃ©m o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_safe_next_url(request):
    """Retorna next seguro para evitar open redirect e loops de login."""
    next_url = request.POST.get('next') or request.GET.get('next')
    if not next_url:
        return None

    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return None

    login_paths = {reverse('usuarios:login'), reverse('usuarios:login_page')}
    if urlparse(next_url).path in login_paths:
        return None

    return next_url


def _build_login_throttle_key(ip_address, scope, value=''):
    fingerprint = salted_hmac(
        key_salt='usuarios.login_throttle',
        value=f'{ip_address}|{scope}|{value.strip().lower()}',
        algorithm='sha256',
    ).hexdigest()
    return f'auth_throttle:{scope}:{fingerprint}'


def _get_lock_until(cache_key):
    state = cache.get(cache_key) or {}
    lock_until = state.get('lock_until')
    if lock_until and timezone.now() < lock_until:
        return lock_until
    return None


def _register_failed_attempt(cache_key, max_attempts):
    now = timezone.now()
    state = cache.get(cache_key) or {'attempts': 0, 'lock_until': None}

    lock_until = state.get('lock_until')
    if lock_until and now >= lock_until:
        state = {'attempts': 0, 'lock_until': None}

    attempts = int(state.get('attempts', 0)) + 1
    state['attempts'] = attempts

    if attempts >= max_attempts:
        state['attempts'] = 0
        state['lock_until'] = now + timedelta(seconds=LOGIN_THROTTLE_LOCKOUT_SECONDS)

    cache_timeout = max(LOGIN_THROTTLE_WINDOW_SECONDS, LOGIN_THROTTLE_LOCKOUT_SECONDS) + 60
    cache.set(cache_key, state, timeout=cache_timeout)
    return state.get('lock_until')


def _reset_failed_attempts(*cache_keys):
    for cache_key in cache_keys:
        cache.delete(cache_key)


def _enforce_password_policy(request, usuario, nova_senha):
    try:
        validate_password(nova_senha, user=usuario)
    except ValidationError as exc:
        for erro in exc.messages:
            messages.error(request, erro)
        return False
    return True


def _build_login_context(request, *, username_value='', remember_me_checked=False):
    return {
        'next': get_safe_next_url(request) or '',
        'username_value': username_value,
        'remember_me_checked': remember_me_checked,
    }


def _tail_log_file(file_path, max_lines):
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return []

    try:
        with path.open('r', encoding='utf-8', errors='ignore') as stream:
            return [line.rstrip() for line in deque(stream, maxlen=max_lines)]
    except OSError:
        return []


def _collect_log_paths():
    logging_cfg = getattr(settings, 'LOGGING', {}) or {}
    handlers_cfg = logging_cfg.get('handlers', {}) or {}

    paths = []
    seen = set()

    for source_name, handler_cfg in handlers_cfg.items():
        filename = handler_cfg.get('filename')
        if not filename:
            continue
        path = Path(filename)
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        paths.append({
            'source': source_name,
            'path': path,
        })

    logs_dir = getattr(settings, 'LOGS_DIR', None)
    if logs_dir:
        for default_name in ('django.log', 'errors.log'):
            default_path = Path(logs_dir) / default_name
            key = str(default_path.resolve()) if default_path.exists() else str(default_path)
            if key in seen:
                continue
            seen.add(key)
            paths.append({
                'source': 'default',
                'path': default_path,
            })

    return paths


def _build_system_logs_snapshot():
    snapshot = []
    for source in _collect_log_paths():
        lines = _tail_log_file(source['path'], AUDIT_LOG_TAIL_LINES)
        snapshot.append({
            'source': source['source'],
            'file_name': source['path'].name,
            'file_path': str(source['path']),
            'exists': source['path'].exists(),
            'line_count': len(lines),
            'lines': lines,
        })
    return snapshot


def _build_active_sessions_snapshot(request):
    now = timezone.now()
    raw_sessions = list(
        Session.objects
        .filter(expire_date__gte=now)
        .order_by('-expire_date')[:AUDIT_SESSIONS_LIMIT]
    )

    decoded_sessions = []
    user_ids = set()
    for session in raw_sessions:
        try:
            payload = session.get_decoded()
        except Exception:
            continue

        raw_user_id = payload.get('_auth_user_id')
        if not raw_user_id:
            continue

        try:
            user_id = int(raw_user_id)
        except (TypeError, ValueError):
            continue

        user_ids.add(user_id)
        decoded_sessions.append((session, user_id, payload))

    users_by_id = Usuario.objects.in_bulk(user_ids)
    current_session_key = request.session.session_key

    rows = []
    for session, user_id, payload in decoded_sessions:
        user = users_by_id.get(user_id)
        if not user:
            continue

        expire_date = session.expire_date
        if timezone.is_aware(expire_date):
            expire_date = timezone.localtime(expire_date)

        rows.append({
            'session_key': session.session_key,
            'session_key_short': f"{session.session_key[:10]}..." if session.session_key else '-',
            'usuario_id': user.id,
            'username': user.username,
            'nome': user.get_full_name() or user.username,
            'email': user.email or '-',
            'nivel_acesso': user.get_nivel_acesso_display(),
            'expira_em': expire_date.strftime('%d/%m/%Y %H:%M'),
            'is_current': bool(current_session_key and session.session_key == current_session_key),
            'auth_login_date': payload.get(DAILY_LOGIN_SESSION_KEY) or '-',
        })

    return rows


def _generate_temporary_password(length=14):
    alphabet = string.ascii_letters + string.digits + '!@#$%*-_'
    while True:
        candidate = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(ch.islower() for ch in candidate)
            and any(ch.isupper() for ch in candidate)
            and any(ch.isdigit() for ch in candidate)
        ):
            return candidate


def _split_full_name(full_name):
    parts = (full_name or '').strip().split()
    if not parts:
        return '', ''
    if len(parts) == 1:
        return parts[0], ''
    return parts[0], ' '.join(parts[1:])


def _parse_boolean_input(raw_value):
    return str(raw_value).strip().lower() in {'1', 'true', 'on', 'yes'}


def _can_manage_developer_accounts(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True

    return (
        (user.email or '').strip().lower() == PRIMARY_DEVELOPER_EMAIL
        or user.username == PRIMARY_DEVELOPER_USERNAME
    )


def _get_auditoria_role_choices(user):
    if _can_manage_developer_accounts(user):
        return list(AUDITORIA_ROLE_CHOICES)
    return [choice for choice in AUDITORIA_ROLE_CHOICES if choice[0] != 'developer']


def login_view(request):
    """View de login com registro de histórico."""
    if request.user.is_authenticated:
        return HttpResponseRedirect(get_safe_next_url(request) or reverse('home'))

    if request.GET.get('session_expired') == '1' or getattr(request, '_daily_session_expired', False):
        messages.info(
            request,
            'Por segurança, sua sessão expirou. Faça login novamente para continuar.',
        )

    if request.method == 'POST':
        credential = (request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        remember_me_checked = request.POST.get('remember_me') in {'on', '1', 'true', 'True'}
        ip_address = get_client_ip(request) or 'unknown'

        credential_throttle_key = _build_login_throttle_key(ip_address, 'credential', credential)
        ip_throttle_key = _build_login_throttle_key(ip_address, 'ip')

        if LOGIN_THROTTLE_ENABLED:
            credential_lock_until = _get_lock_until(credential_throttle_key)
            ip_lock_until = _get_lock_until(ip_throttle_key)
            active_lock_until = max(
                [lock for lock in [credential_lock_until, ip_lock_until] if lock],
                default=None,
            )

            if active_lock_until:
                minutos_restantes = max(
                    1,
                    ceil((active_lock_until - timezone.now()).total_seconds() / 60),
                )
                messages.error(
                    request,
                    f'Muitas tentativas de login. Tente novamente em {minutos_restantes} minuto(s).',
                )
                logger.warning(
                    'Login bloqueado por throttle. ip=%s credencial=%s',
                    ip_address,
                    credential,
                )
                return render(
                    request,
                    'login.html',
                    _build_login_context(
                        request,
                        username_value=credential,
                        remember_me_checked=remember_me_checked,
                    ),
                )

        user = auth_authenticate(request, username=credential, password=password)

        user_for_audit = None

        # Permite autenticar também via email ou nome completo (quando único).
        if user is None and credential:
            user_for_audit = Usuario.objects.filter(email__iexact=credential).first()
            if user_for_audit is None and ' ' in credential:
                parts = credential.split()
                first_name = parts[0]
                last_name = ' '.join(parts[1:])
                matches = list(
                    Usuario.objects.filter(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                    )[:2]
                )
                if len(matches) == 1:
                    user_for_audit = matches[0]

            if user_for_audit:
                user = auth_authenticate(
                    request,
                    username=user_for_audit.username,
                    password=password,
                )

        if user is not None:
            if user.ativo:
                auth_login(request, user)
                # Sessão sempre expira ao fechar o navegador.
                request.session.set_expiry(0)
                # Controle adicional para exigir novo login em um novo dia.
                request.session[DAILY_LOGIN_SESSION_KEY] = timezone.localdate().isoformat()

                if LOGIN_THROTTLE_ENABLED:
                    _reset_failed_attempts(credential_throttle_key, ip_throttle_key)

                HistoricoAcesso.objects.create(
                    usuario=user,
                    tipo_acao='login',
                    descricao='Login bem-sucedido',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
                next_url = get_safe_next_url(request)
                if next_url:
                    return HttpResponseRedirect(next_url)
                return HttpResponseRedirect(reverse('home'))
            else:
                logger.warning(
                    "Login bloqueado: conta desativada. credencial=%s usuario=%s",
                    credential,
                    user.username,
                )
                if LOGIN_THROTTLE_ENABLED:
                    _register_failed_attempt(credential_throttle_key, LOGIN_THROTTLE_MAX_ATTEMPTS)
                    _register_failed_attempt(ip_throttle_key, LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP)
                messages.error(request, 'Sua conta está desativada.')
        else:
            try:
                user_tentativa = Usuario.objects.get(username=credential)
                HistoricoAcesso.objects.create(
                    usuario=user_tentativa,
                    tipo_acao='login_falho',
                    descricao='Tentativa de login com senha incorreta',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                logger.warning(
                    "Login falhou: senha incorreta via username. credencial=%s usuario=%s",
                    credential,
                    user_tentativa.username,
                )
            except Usuario.DoesNotExist:
                user_tentativa = user_for_audit
                if user_tentativa:
                    HistoricoAcesso.objects.create(
                        usuario=user_tentativa,
                        tipo_acao='login_falho',
                        descricao='Tentativa de login com senha incorreta',
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                    )
                    logger.warning(
                        "Login falhou: senha incorreta via email/nome. credencial=%s usuario=%s",
                        credential,
                        user_tentativa.username,
                    )
                else:
                    logger.warning(
                        "Login falhou: usuario nao encontrado. credencial=%s",
                        credential,
                    )
            active_lock_until = None
            if LOGIN_THROTTLE_ENABLED:
                credential_lock_until = _register_failed_attempt(
                    credential_throttle_key,
                    LOGIN_THROTTLE_MAX_ATTEMPTS,
                )
                ip_lock_until = _register_failed_attempt(
                    ip_throttle_key,
                    LOGIN_THROTTLE_MAX_ATTEMPTS_PER_IP,
                )
                active_lock_until = max(
                    [lock for lock in [credential_lock_until, ip_lock_until] if lock],
                    default=None,
                )

            if active_lock_until:
                minutos_restantes = max(
                    1,
                    ceil((active_lock_until - timezone.now()).total_seconds() / 60),
                )
                messages.error(
                    request,
                    f'Número máximo de tentativas atingido. Tente novamente em {minutos_restantes} minuto(s).',
                )
            else:
                messages.error(request, 'Usuário ou senha incorretos.')

        return render(
            request,
            'login.html',
            _build_login_context(
                request,
                username_value=credential,
                remember_me_checked=remember_me_checked,
            ),
        )

    context = _build_login_context(request)
    return render(request, 'login.html', context)


@login_required
def logout_view(request):
    """View de logout com registro de histÃ³rico"""
    HistoricoAcesso.objects.create(
        usuario=request.user,
        tipo_acao='logout',
        descricao='Logout',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    auth_logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return HttpResponseRedirect(reverse('usuarios:login'))


def recuperar_senha_view(request):
    """Solicita recuperaÃ§Ã£o de senha"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email, ativo=True)
            _, token = TokenRecuperacaoSenha.criar_token(usuario=usuario)
            reset_url = request.build_absolute_uri(
                reverse('usuarios:resetar_senha', kwargs={'token': token})
            )
            assunto = 'RecuperaÃ§Ã£o de Senha - SuplaStock'
            mensagem = f"""
Olá¡ {usuario.get_full_name() or usuario.username},

Recebemos uma solicitação de recuperaÃ§Ã£o de senha para sua conta.

Clique no link abaixo para criar uma nova senha:
{reset_url}

Este link Ã© vÃ¡lido por 24 horas.

Se vocÃª nÃ£o solicitou esta recuperaÃ§Ã£o, ignore este e-mail.

Atenciosamente,
Equipe SuplaStock
            """
            send_mail(
                assunto,
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'InstruÃ§Ãµes de recuperaÃ§Ã£o foram enviadas para seu e-mail.')
            return HttpResponseRedirect(reverse('usuarios:login'))
        except Usuario.DoesNotExist:
            messages.success(request, 'Se o e-mail estiver cadastrado, vocÃª receberÃ¡ instruÃ§Ãµes de recuperaÃ§Ã£o.')
            return HttpResponseRedirect(reverse('usuarios:login'))
    return render(request, 'usuarios/auth/recuperar_senha.html')


def resetar_senha_view(request, token):
    """Reseta a senha usando o token"""
    token_obj = TokenRecuperacaoSenha.buscar_por_token(token)

    if not token_obj or not token_obj.is_valido():
        messages.error(request, 'Link de recuperaÃ§Ã£o invÃ¡lido.')
        return HttpResponseRedirect(reverse('usuarios:login'))

    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            messages.error(request, 'As senhas nÃ£o coincidem.')
        elif not _enforce_password_policy(request, token_obj.usuario, nova_senha):
            pass
        else:
            usuario = token_obj.usuario
            usuario.set_password(nova_senha)
            usuario.save()

            # Invalida todos os tokens pendentes do usuÃ¡rio apÃ³s troca bem-sucedida.
            TokenRecuperacaoSenha.objects.filter(usuario=usuario, usado=False).update(usado=True)

            HistoricoAcesso.objects.create(
                usuario=usuario,
                tipo_acao='editar',
                descricao='Senha alterada via recuperaÃ§Ã£o',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            messages.success(request, 'Senha alterada com sucesso! FaÃ§a login com sua nova senha.')
            return HttpResponseRedirect(reverse('usuarios:login'))

    return render(request, 'usuarios/auth/resetar_senha.html', {'token': token})


@login_required
def alterar_senha_view(request):
    """Permite usuÃ¡rio logado alterar sua prÃ³pria senha"""
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        if not request.user.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
        elif nova_senha != confirmar_senha:
            messages.error(request, 'As novas senhas nÃ£o coincidem.')
        elif not _enforce_password_policy(request, request.user, nova_senha):
            pass
        else:
            request.user.set_password(nova_senha)
            request.user.save()
            HistoricoAcesso.objects.create(
                usuario=request.user,
                tipo_acao='editar',
                descricao='Senha alterada pelo prÃ³prio usuÃ¡rio',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Senha alterada com sucesso!')
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'usuarios/auth/alterar_senha.html')


@developer_requerido
def auditoria_view(request):
    """Painel de auditoria e seguranca. Acesso apenas para developer/auditor."""
    filtro_busca = (request.GET.get('q') or '').strip()
    filtro_nivel = (request.GET.get('nivel') or '').strip()
    filtro_status = (request.GET.get('status') or '').strip()

    usuarios_base = Usuario.objects.annotate(
        total_eventos=Count('historico_acessos'),
        ultimo_evento=Max('historico_acessos__data_hora'),
    )
    usuarios = usuarios_base

    if filtro_busca:
        usuarios = usuarios.filter(
            Q(username__icontains=filtro_busca)
            | Q(email__icontains=filtro_busca)
            | Q(first_name__icontains=filtro_busca)
            | Q(last_name__icontains=filtro_busca)
        )

    all_roles = {choice[0] for choice in AUDITORIA_ROLE_CHOICES}
    if filtro_nivel and filtro_nivel in all_roles:
        usuarios = usuarios.filter(nivel_acesso=filtro_nivel)

    if filtro_status == 'ativo':
        usuarios = usuarios.filter(ativo=True)
    elif filtro_status == 'inativo':
        usuarios = usuarios.filter(ativo=False)

    usuarios = usuarios.order_by('-is_superuser', '-is_staff', 'first_name', 'username')

    historico_qs = (
        HistoricoAcesso.objects
        .select_related('usuario')
        .order_by('-data_hora')
    )

    acessos_qs = historico_qs.filter(tipo_acao__in=['login', 'logout', 'login_falho'])
    acoes_qs = historico_qs.exclude(tipo_acao__in=['login', 'logout', 'login_falho'])

    acessos_page_obj = Paginator(acessos_qs, 10).get_page(request.GET.get('acessos_page', 1))
    acoes_page_obj = Paginator(acoes_qs, 10).get_page(request.GET.get('acoes_page', 1))

    sessoes_ativas_raw = _build_active_sessions_snapshot(request)
    sessoes_page_obj = Paginator(sessoes_ativas_raw, 10).get_page(request.GET.get('sessoes_page', 1))
    sessoes_ativas = list(sessoes_page_obj.object_list)

    active_logs_tab = (request.GET.get('tab') or 'acessos').strip().lower()
    if active_logs_tab not in {'acessos', 'acoes'}:
        active_logs_tab = 'acessos'

    query_for_pagination = request.GET.copy()
    for key in ('acessos_page', 'acoes_page', 'sessoes_page', 'tab'):
        if key in query_for_pagination:
            del query_for_pagination[key]
    auditoria_filters_query = query_for_pagination.urlencode()

    logs_sistema = _build_system_logs_snapshot()
    senha_temporaria = request.session.pop('auditoria_password_reset_result', None)
    novo_usuario_form = request.session.pop('auditoria_create_user_form', None) or {}
    auditoria_open_modal = request.session.pop('auditoria_open_modal', '')
    role_choices = _get_auditoria_role_choices(request.user)
    role_labels = dict(AUDITORIA_ROLE_CHOICES)

    context = {
        'historico_recente': historico_qs[:AUDIT_HISTORY_LIMIT],
        'acessos_recentes': list(acessos_page_obj.object_list),
        'acoes_recentes': list(acoes_page_obj.object_list),
        'acessos_page_obj': acessos_page_obj,
        'acoes_page_obj': acoes_page_obj,
        'usuarios': usuarios,
        'sessoes_ativas': sessoes_ativas,
        'sessoes_page_obj': sessoes_page_obj,
        'logs_sistema': logs_sistema,
        'senha_temporaria': senha_temporaria,
        'total_usuarios': usuarios_base.count(),
        'total_usuarios_ativos': usuarios_base.filter(ativo=True).count(),
        'total_developers': usuarios_base.filter(nivel_acesso='developer').count(),
        'total_admins': usuarios_base.filter(nivel_acesso='admin').count(),
        'total_vendedores': usuarios_base.filter(nivel_acesso='vendedor').count(),
        'usuarios_filtrados_count': usuarios.count(),
        'filtro_busca': filtro_busca,
        'filtro_nivel': filtro_nivel,
        'filtro_status': filtro_status,
        'role_choices': role_choices,
        'role_labels': role_labels,
        'can_manage_developer': _can_manage_developer_accounts(request.user),
        'active_logs_tab': active_logs_tab,
        'auditoria_filters_query': auditoria_filters_query,
        'novo_usuario_form': novo_usuario_form,
        'auditoria_open_modal': auditoria_open_modal,
    }
    return render(request, 'usuarios/auditoria.html', context)


@developer_requerido
@require_POST
@transaction.atomic
def auditoria_criar_usuario(request):
    """Cria usuario pela tela de auditoria."""
    nome_completo = (request.POST.get('nome_completo') or '').strip()
    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip().lower()
    senha_inicial = request.POST.get('senha_inicial') or ''
    confirmar_senha = request.POST.get('confirmar_senha') or ''
    nivel_acesso = (request.POST.get('nivel_acesso') or '').strip()
    ativo = _parse_boolean_input(request.POST.get('ativo'))
    create_form_state = {
        'nome_completo': nome_completo,
        'username': username,
        'email': email,
        'nivel_acesso': nivel_acesso,
        'ativo': ativo,
    }

    def _redirect_with_form_error(message):
        request.session['auditoria_create_user_form'] = create_form_state
        request.session['auditoria_open_modal'] = 'novo_usuario'
        messages.error(request, message)
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if not nome_completo or not username or not email or not senha_inicial:
        return _redirect_with_form_error('Preencha todos os campos obrigatorios do novo usuario.')

    if senha_inicial != confirmar_senha:
        return _redirect_with_form_error('A confirmacao de senha nao confere.')

    allowed_roles = dict(_get_auditoria_role_choices(request.user))
    if nivel_acesso not in allowed_roles:
        return _redirect_with_form_error('Perfil selecionado nao permitido para o seu usuario.')

    if nivel_acesso == 'developer' and not _can_manage_developer_accounts(request.user):
        return _redirect_with_form_error('Apenas o desenvolvedor principal pode criar outro perfil developer.')

    if Usuario.objects.filter(username__iexact=username).exists():
        return _redirect_with_form_error('Ja existe um usuario com esse username.')

    if Usuario.objects.filter(email__iexact=email).exists():
        return _redirect_with_form_error('Ja existe um usuario com esse e-mail.')

    first_name, last_name = _split_full_name(nome_completo)
    usuario_novo = Usuario(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        nivel_acesso=nivel_acesso,
        ativo=ativo,
        is_active=ativo,
        is_staff=nivel_acesso in {'admin', 'developer'},
    )

    try:
        validate_password(senha_inicial, user=usuario_novo)
    except ValidationError as exc:
        for erro in exc.messages:
            messages.error(request, erro)
        request.session['auditoria_create_user_form'] = create_form_state
        request.session['auditoria_open_modal'] = 'novo_usuario'
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    usuario_novo.set_password(senha_inicial)
    usuario_novo.save()
    request.session.pop('auditoria_create_user_form', None)
    request.session.pop('auditoria_open_modal', None)

    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    HistoricoAcesso.objects.create(
        usuario=request.user,
        tipo_acao='criar',
        descricao=f'Criou usuario {usuario_novo.username} com perfil {usuario_novo.get_nivel_acesso_display()}.',
        ip_address=ip_address,
        user_agent=user_agent,
        modelo_afetado='Usuario',
        objeto_id=usuario_novo.id,
        dados_adicionais={
            'target_username': usuario_novo.username,
            'target_email': usuario_novo.email,
            'target_nivel': usuario_novo.nivel_acesso,
            'target_ativo': usuario_novo.ativo,
        },
    )

    messages.success(
        request,
        f'Usuario {usuario_novo.get_full_name() or usuario_novo.username} criado com sucesso.',
    )
    return HttpResponseRedirect(reverse('usuarios:auditoria'))


@developer_requerido
@require_POST
@transaction.atomic
def auditoria_atualizar_usuario(request, usuario_id):
    """Atualiza perfil e status de usuario pela auditoria."""
    usuario_alvo = get_object_or_404(Usuario, id=usuario_id)

    nome_completo = (request.POST.get('nome_completo') or '').strip()
    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip().lower()
    nivel_acesso = (request.POST.get('nivel_acesso') or '').strip()
    ativo = _parse_boolean_input(request.POST.get('ativo'))

    if not nome_completo or not username or not email:
        messages.error(request, 'Nome, username e e-mail sao obrigatorios.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    allowed_roles = dict(_get_auditoria_role_choices(request.user))
    if nivel_acesso not in allowed_roles:
        messages.error(request, 'Perfil selecionado nao permitido para o seu usuario.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if (
        (nivel_acesso == 'developer' or usuario_alvo.nivel_acesso == 'developer')
        and not _can_manage_developer_accounts(request.user)
    ):
        messages.error(request, 'Apenas o desenvolvedor principal pode alterar contas developer.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.id == request.user.id and nivel_acesso != 'developer':
        messages.error(request, 'Seu proprio perfil nao pode ser rebaixado por esta tela.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.id == request.user.id and not ativo:
        messages.error(request, 'Nao e permitido desativar o proprio usuario.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if Usuario.objects.filter(username__iexact=username).exclude(id=usuario_alvo.id).exists():
        messages.error(request, 'Ja existe outro usuario com esse username.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if Usuario.objects.filter(email__iexact=email).exclude(id=usuario_alvo.id).exists():
        messages.error(request, 'Ja existe outro usuario com esse e-mail.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    first_name, last_name = _split_full_name(nome_completo)
    alteracoes = {}

    def _track(field, old_value, new_value):
        if old_value != new_value:
            alteracoes[field] = {
                'de': old_value,
                'para': new_value,
            }

    _track('first_name', usuario_alvo.first_name, first_name)
    _track('last_name', usuario_alvo.last_name, last_name)
    _track('username', usuario_alvo.username, username)
    _track('email', usuario_alvo.email or '', email)
    _track('nivel_acesso', usuario_alvo.nivel_acesso, nivel_acesso)
    _track('ativo', bool(usuario_alvo.ativo), bool(ativo))

    usuario_alvo.first_name = first_name
    usuario_alvo.last_name = last_name
    usuario_alvo.username = username
    usuario_alvo.email = email
    usuario_alvo.nivel_acesso = nivel_acesso
    usuario_alvo.ativo = ativo
    usuario_alvo.is_active = ativo
    usuario_alvo.is_staff = nivel_acesso in {'admin', 'developer'}
    usuario_alvo.save()

    if alteracoes:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        HistoricoAcesso.objects.create(
            usuario=request.user,
            tipo_acao='editar',
            descricao=f'Atualizou usuario {usuario_alvo.username}.',
            ip_address=ip_address,
            user_agent=user_agent,
            modelo_afetado='Usuario',
            objeto_id=usuario_alvo.id,
            dados_adicionais=alteracoes,
        )
        HistoricoAcesso.objects.create(
            usuario=usuario_alvo,
            tipo_acao='editar',
            descricao='Perfil/Status atualizado por desenvolvedor/auditor.',
            ip_address=ip_address,
            user_agent=user_agent,
            modelo_afetado='Usuario',
            objeto_id=usuario_alvo.id,
            dados_adicionais={
                'updated_by': request.user.username,
                'fields_changed': list(alteracoes.keys()),
            },
        )
        messages.success(request, f'Usuario {usuario_alvo.username} atualizado com sucesso.')
    else:
        messages.info(request, 'Nenhuma alteracao detectada para salvar.')

    return HttpResponseRedirect(reverse('usuarios:auditoria'))


@developer_requerido
@require_POST
@transaction.atomic
def auditoria_resetar_senha_usuario(request, usuario_id):
    """Permite ao developer redefinir senha de qualquer usuario."""
    usuario_alvo = get_object_or_404(Usuario, id=usuario_id)
    if usuario_alvo.id == request.user.id:
        messages.error(request, 'Use a tela de alterar senha para redefinir sua propria senha.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.nivel_acesso == 'developer' and not _can_manage_developer_accounts(request.user):
        messages.error(request, 'Apenas o desenvolvedor principal pode redefinir senha de outra conta developer.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    nova_senha = (request.POST.get('nova_senha') or '').strip()
    confirmar_senha = (request.POST.get('confirmar_senha') or '').strip()

    if nova_senha and nova_senha != confirmar_senha:
        messages.error(request, 'A confirmacao da nova senha nao confere.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    senha_gerada_automaticamente = False
    if not nova_senha:
        nova_senha = _generate_temporary_password()
        senha_gerada_automaticamente = True

    try:
        validate_password(nova_senha, user=usuario_alvo)
    except ValidationError as exc:
        for erro in exc.messages:
            messages.error(request, erro)
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    usuario_alvo.set_password(nova_senha)
    usuario_alvo.save()

    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    HistoricoAcesso.objects.create(
        usuario=request.user,
        tipo_acao='editar',
        descricao=f'Redefiniu senha do usuario {usuario_alvo.username}.',
        ip_address=ip_address,
        user_agent=user_agent,
        modelo_afetado='Usuario',
        objeto_id=usuario_alvo.id,
        dados_adicionais={
            'target_username': usuario_alvo.username,
            'target_email': usuario_alvo.email,
            'target_nivel': usuario_alvo.nivel_acesso,
            'password_generated': senha_gerada_automaticamente,
        },
    )
    HistoricoAcesso.objects.create(
        usuario=usuario_alvo,
        tipo_acao='editar',
        descricao='Senha redefinida por desenvolvedor/auditor.',
        ip_address=ip_address,
        user_agent=user_agent,
        modelo_afetado='Usuario',
        objeto_id=usuario_alvo.id,
        dados_adicionais={
            'reset_by': request.user.username,
        },
    )

    messages.success(
        request,
        f'Senha de {usuario_alvo.get_full_name() or usuario_alvo.username} redefinida com sucesso.',
    )
    if senha_gerada_automaticamente:
        request.session['auditoria_password_reset_result'] = {
            'usuario_nome': usuario_alvo.get_full_name() or usuario_alvo.username,
            'usuario_username': usuario_alvo.username,
            'senha_temporaria': nova_senha,
        }
        messages.info(
            request,
            'Senha provisoria gerada automaticamente. Copie o valor exibido no painel de auditoria.',
        )

    return HttpResponseRedirect(reverse('usuarios:auditoria'))


@developer_requerido
@require_POST
@transaction.atomic
def auditoria_deletar_usuario(request, usuario_id):
    """Permite ao developer excluir usuario com confirmacao e trilha de auditoria."""
    usuario_alvo = get_object_or_404(Usuario, id=usuario_id)

    if usuario_alvo.id == request.user.id:
        messages.error(request, 'Nao e permitido excluir o proprio usuario.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.nivel_acesso == 'developer' and not _can_manage_developer_accounts(request.user):
        messages.error(request, 'Apenas o desenvolvedor principal pode excluir outra conta developer.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.is_superuser and not request.user.is_superuser:
        messages.error(request, 'Apenas superusuario pode excluir outra conta superusuario.')
        return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.nivel_acesso == 'developer':
        developers_restantes = Usuario.objects.filter(nivel_acesso='developer').exclude(id=usuario_alvo.id).count()
        if developers_restantes <= 0:
            messages.error(request, 'Nao e permitido excluir a ultima conta developer do sistema.')
            return HttpResponseRedirect(reverse('usuarios:auditoria'))

    if usuario_alvo.is_superuser:
        superusers_restantes = Usuario.objects.filter(is_superuser=True).exclude(id=usuario_alvo.id).count()
        if superusers_restantes <= 0:
            messages.error(request, 'Nao e permitido excluir o ultimo superusuario do sistema.')
            return HttpResponseRedirect(reverse('usuarios:auditoria'))

    target_data = {
        'target_id': usuario_alvo.id,
        'target_username': usuario_alvo.username,
        'target_nome': usuario_alvo.get_full_name() or usuario_alvo.username,
        'target_email': usuario_alvo.email or '',
        'target_nivel': usuario_alvo.nivel_acesso,
        'target_is_superuser': bool(usuario_alvo.is_superuser),
        'target_is_staff': bool(usuario_alvo.is_staff),
        'target_ativo': bool(usuario_alvo.ativo),
    }

    usuario_excluido_nome = target_data['target_nome']
    usuario_excluido_username = target_data['target_username']
    usuario_alvo.delete()

    HistoricoAcesso.objects.create(
        usuario=request.user,
        tipo_acao='deletar',
        descricao=f'Excluiu usuario {usuario_excluido_username}.',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        modelo_afetado='Usuario',
        objeto_id=target_data['target_id'],
        dados_adicionais=target_data,
    )

    messages.success(request, f'Usuario {usuario_excluido_nome} excluido com sucesso.')
    return HttpResponseRedirect(reverse('usuarios:auditoria'))


@login_required
def perfil_view(request):
    """View do perfil do usuÃ¡rio"""
    ultimos_acessos = HistoricoAcesso.objects.filter(
        usuario=request.user
    ).order_by('-data_hora')[:10]
    context = {
        'ultimos_acessos': ultimos_acessos,
    }
    return render(request, 'usuarios/auth/perfil.html', context)


@login_required
def home_view(request):
    """View da página inicial (Acesso Rápido)"""
    return render(request, 'landing/index.html')

