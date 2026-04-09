from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def _role_required(check_fn, *, allow_superuser=True):
    def decorator(view_func):
        @login_required(login_url='usuarios:login')
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if (allow_superuser and getattr(user, 'is_superuser', False)) or check_fn(user):
                return view_func(request, *args, **kwargs)

            messages.error(request, 'Você não tem permissão para acessar essa funcionalidade.')
            return redirect('home')

        return _wrapped

    return decorator


def _has_admin_scope(user):
    return (
        getattr(user, 'is_admin', False)
        or getattr(user, 'is_developer', False)
        or getattr(user, 'is_superuser', False)
    )


def admin_requerido(function=None):
    actual_decorator = _role_required(
        lambda u: _has_admin_scope(u),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def vendedor_ou_admin(function=None):
    actual_decorator = _role_required(
        lambda u: getattr(u, 'is_vendedor', False) or _has_admin_scope(u),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def estoquista_ou_admin(function=None):
    actual_decorator = _role_required(
        lambda u: getattr(u, 'is_estoquista', False) or _has_admin_scope(u),
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def developer_requerido(function=None):
    actual_decorator = _role_required(
        lambda u: getattr(u, 'is_developer', False),
        allow_superuser=False,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
