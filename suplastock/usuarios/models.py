from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.crypto import salted_hmac
from datetime import timedelta
import secrets


class Usuario(AbstractUser):
    """
    Modelo customizado de usuário com níveis de permissão
    """
    NIVEL_CHOICES = [
        ('admin', 'Administrador'),
        ('developer', 'Desenvolvedor / Auditor'),
        ('vendedor', 'Vendedor'),
        ('estoquista', 'Estoquista'),
    ]

    nivel_acesso = models.CharField(max_length=20, choices=NIVEL_CHOICES, default='vendedor')
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-date_joined']
        db_table = 'gestao_usuario'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_nivel_acesso_display()})"

    @property
    def is_admin(self):
        return self.nivel_acesso == 'admin'

    @property
    def is_developer(self):
        return self.nivel_acesso == 'developer'

    @property
    def has_full_operational_access(self):
        return self.is_admin or self.is_developer or self.is_superuser

    @property
    def is_vendedor(self):
        return self.nivel_acesso == 'vendedor'

    @property
    def is_estoquista(self):
        return self.nivel_acesso == 'estoquista'


class HistoricoAcesso(models.Model):
    """
    Registra todos os acessos e ações importantes do sistema
    """
    TIPO_ACAO_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_falho', 'Tentativa de Login Falha'),
        ('criar', 'Criação'),
        ('editar', 'Edição'),
        ('deletar', 'Exclusão'),
        ('visualizar', 'Visualização'),
    ]

    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='historico_acessos')
    tipo_acao = models.CharField(max_length=20, choices=TIPO_ACAO_CHOICES)
    descricao = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    # Dados adicionais
    modelo_afetado = models.CharField(max_length=100, blank=True, null=True,
                                      help_text="Modelo que foi afetado pela ação")
    objeto_id = models.IntegerField(null=True, blank=True,
                                    help_text="ID do objeto afetado")
    dados_adicionais = models.JSONField(null=True, blank=True,
                                        help_text="Dados extras em JSON")

    class Meta:
        verbose_name = 'Histórico de Acesso'
        verbose_name_plural = 'Históricos de Acessos'
        ordering = ['-data_hora']
        db_table = 'gestao_historicoacesso'
        indexes = [
            models.Index(fields=['-data_hora']),
            models.Index(fields=['usuario', '-data_hora']),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_acao_display()} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class TokenRecuperacaoSenha(models.Model):
    """
    Tokens para recuperação de senha
    """
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    expira_em = models.DateTimeField()

    class Meta:
        verbose_name = 'Token de Recuperação'
        verbose_name_plural = 'Tokens de Recuperação'
        db_table = 'gestao_tokenrecuperacaosenha'

    def __str__(self):
        return f"Token para {self.usuario.username}"

    def is_valido(self):
        """Verifica se o token ainda é válido"""
        return not self.usado and timezone.now() < self.expira_em

    @classmethod
    def hash_token(cls, raw_token):
        """Gera hash determinístico do token para persistência segura."""
        return salted_hmac(
            key_salt='usuarios.TokenRecuperacaoSenha',
            value=str(raw_token),
            algorithm='sha256',
        ).hexdigest()

    @classmethod
    def criar_token(cls, usuario, expira_em=None):
        """
        Cria novo token de recuperação em formato seguro.

        Retorna uma tupla com o objeto salvo e o token em texto puro
        (apenas para envio por e-mail).
        """
        # Invalida tokens pendentes anteriores para reduzir janela de abuso.
        cls.objects.filter(usuario=usuario, usado=False).update(usado=True)

        raw_token = secrets.token_urlsafe(32)
        token_hash = cls.hash_token(raw_token)
        while cls.objects.filter(token=token_hash).exists():
            raw_token = secrets.token_urlsafe(32)
            token_hash = cls.hash_token(raw_token)

        token_obj = cls.objects.create(
            usuario=usuario,
            token=token_hash,
            expira_em=expira_em or (timezone.now() + timedelta(hours=24)),
        )
        return token_obj, raw_token

    @classmethod
    def buscar_por_token(cls, raw_token):
        """
        Busca token válido por valor em texto puro.

        Compatível com legado: se encontrar token antigo em texto puro,
        converte para hash no primeiro uso.
        """
        token_hash = cls.hash_token(raw_token)
        token_obj = cls.objects.filter(token=token_hash).select_related('usuario').first()
        if token_obj:
            return token_obj

        # Compatibilidade temporária com tokens históricos em texto puro.
        legacy = cls.objects.filter(token=raw_token).select_related('usuario').first()
        if legacy:
            legacy.token = token_hash
            try:
                legacy.save(update_fields=['token'])
            except IntegrityError:
                # Em caso de colisão/concorrência, mantém token legado para evitar erro 500.
                pass
        return legacy

    def save(self, *args, **kwargs):
        """Define expiração automaticamente (24 horas)"""
        if not self.expira_em:
            self.expira_em = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
