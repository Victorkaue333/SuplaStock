from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_page'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('auth/resetar-senha/<str:token>/', views.resetar_senha_view, name='resetar_senha'),
    path('auth/alterar-senha/', views.alterar_senha_view, name='alterar_senha'),
    path('auth/perfil/', views.perfil_view, name='perfil'),
    path('auth/auditoria/', views.auditoria_view, name='auditoria'),
    path('auth/auditoria/usuarios/criar/', views.auditoria_criar_usuario, name='auditoria_criar_usuario'),
    path(
        'auth/auditoria/usuarios/<int:usuario_id>/atualizar/',
        views.auditoria_atualizar_usuario,
        name='auditoria_atualizar_usuario',
    ),
    path(
        'auth/auditoria/usuarios/<int:usuario_id>/resetar-senha/',
        views.auditoria_resetar_senha_usuario,
        name='auditoria_resetar_senha_usuario',
    ),
    path(
        'auth/auditoria/usuarios/<int:usuario_id>/deletar/',
        views.auditoria_deletar_usuario,
        name='auditoria_deletar_usuario',
    ),
]
