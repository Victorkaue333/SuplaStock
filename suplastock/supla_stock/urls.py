
"""
URL configuration for suplastock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import RedirectView
from usuarios.views import home_view


def liveness_probe(_request):
    """
    Healthcheck de liveness para plataforma (nÃ£o depende de banco/cache/storage).
    """
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'favicon.ico',
        RedirectView.as_view(url=f'{settings.STATIC_URL}img/favicon.ico', permanent=True),
        name='favicon',
    ),

    # Health Check
    path('health/', include('health_check.urls')),
    path('healthz/', liveness_probe, name='healthz'),

    # Home
    path('home/', home_view, name='home'),
    path('', include('dashboard.urls')),

    # Apps modulares
    path('', include('usuarios.urls')),
    path('', include('estoque.urls')),
    path('', include('vendas.urls')),
    path('', include('financeiro.urls')),
]

# Servir arquivos de mÃ­dia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

