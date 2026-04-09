from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, HistoricoAcesso, TokenRecuperacaoSenha


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'get_full_name', 'nivel_acesso', 'ativo', 'date_joined']
    list_filter = ['nivel_acesso', 'ativo', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('nivel_acesso', 'telefone', 'foto_perfil', 'ativo')
        }),
    )


@admin.register(HistoricoAcesso)
class HistoricoAcessoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_acao', 'descricao', 'ip_address', 'data_hora']
    list_filter = ['tipo_acao', 'data_hora']
    search_fields = ['usuario__username', 'descricao', 'ip_address']
    date_hierarchy = 'data_hora'
    readonly_fields = ['usuario', 'tipo_acao', 'descricao', 'ip_address', 'user_agent', 'data_hora']


@admin.register(TokenRecuperacaoSenha)
class TokenRecuperacaoSenhaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'token', 'criado_em', 'expira_em', 'usado']
    list_filter = ['usado', 'criado_em']
    search_fields = ['usuario__username', 'token']
    readonly_fields = ['token', 'criado_em']
