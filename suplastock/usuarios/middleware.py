from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone


class DailyReauthenticationMiddleware:
    """
    Garante reautenticação diária.

    Regra:
    - Se o usuário autenticado atravessar para um novo dia de calendário,
      a sessão é encerrada e o login volta a ser obrigatório.
    """

    LOGIN_DATE_SESSION_KEY = 'auth_login_date'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            hoje = timezone.localdate().isoformat()
            login_date = request.session.get(self.LOGIN_DATE_SESSION_KEY)

            if login_date and login_date != hoje:
                auth_logout(request)
                request._daily_session_expired = True

                login_urls = {reverse('usuarios:login'), reverse('usuarios:login_page')}
                if request.path not in login_urls:
                    return HttpResponseRedirect(f"{reverse('usuarios:login')}?session_expired=1")
            elif not login_date:
                request.session[self.LOGIN_DATE_SESSION_KEY] = hoje

        return self.get_response(request)
