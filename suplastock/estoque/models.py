# estoque/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime


class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        db_table = 'gestao_categoria'

    def __str__(self):
        return self.nome


class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'gestao_fornecedor'
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=255)
    sku = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
        null=True,
        help_text="Código único do produto",
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True,
                                   help_text="Fornecedor principal do produto")
    fornecedor_nome_legado = models.CharField(max_length=255, blank=True, null=True,
                                              help_text="Nome do fornecedor em produtos antigos")

    # Estoque
    quantidade_comprada = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    estoque_atual = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    estoque_minimo = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        help_text="Quantidade mínima para alerta",
    )

    # Lote e Validade
    lote = models.CharField(max_length=100, blank=True, null=True)
    data_fabricacao = models.DateField(null=True, blank=True)
    data_validade = models.DateField(null=True, blank=True)

    # Preços e Custos
    preco_custo_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    preco_venda_sugerido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
    )
    margem_lucro_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                  help_text="Margem de lucro em %")

    # Metadados
    data_compra = models.DateField()
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gestao_produto'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome

    @property
    def estoque_baixo(self):
        return self.estoque_atual <= self.estoque_minimo

    @property
    def status_estoque_codigo(self):
        estoque_atual = int(self.estoque_atual or 0)
        estoque_minimo = int(self.estoque_minimo or 0)
        if estoque_atual == 0:
            return 'esgotado'
        if estoque_atual <= estoque_minimo:
            return 'critico'
        if estoque_atual <= (estoque_minimo + 3):
            return 'baixo'
        return 'normal'

    @property
    def status_estoque(self):
        rotulos = {
            'normal': 'NORMAL',
            'baixo': 'BAIXO',
            'critico': 'CRÍTICO',
            'esgotado': 'ESGOTADO',
        }
        return rotulos.get(self.status_estoque_codigo, 'NORMAL')

    @property
    def quantidade_total_vendida(self):
        from vendas.models import Venda

        agregado = (
            Venda.objects
            .filter(produto_id=self.id)
            .aggregate(total=Sum('quantidade_vendida'))
        )
        return int(agregado.get('total') or 0)

    @property
    def dias_para_vencer(self):
        if self.data_validade:
            delta = self.data_validade - datetime.now().date()
            return delta.days
        return None

    @property
    def vencido(self):
        if self.data_validade:
            return datetime.now().date() > self.data_validade
        return False

    @property
    def proximo_vencimento(self):
        dias = self.dias_para_vencer
        return dias is not None and 0 < dias <= 30

    @property
    def lucro_unitario(self):
        return Decimal(str(self.preco_venda_sugerido)) - Decimal(str(self.preco_custo_unitario))

    def calcular_margem_lucro(self):
        preco_custo = Decimal(str(self.preco_custo_unitario))
        preco_venda = Decimal(str(self.preco_venda_sugerido))
        if preco_custo > 0:
            margem = ((preco_venda - preco_custo) / preco_custo) * Decimal('100')
            return margem
        return Decimal('0')

    def save(self, *args, **kwargs):
        self.margem_lucro_percentual = self.calcular_margem_lucro()
        if not self.sku:
            self.sku = self._gerar_sku_unico()
        super().save(*args, **kwargs)

    def _gerar_sku_unico(self):
        base = ''.join(ch for ch in (self.nome or '').upper() if ch.isalnum())[:3] or 'PRD'
        sequencia = 1
        while True:
            candidato = f'{base}-{sequencia:03d}'
            conflitos = Produto.objects.filter(sku=candidato)
            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)
            if not conflitos.exists():
                return candidato
            sequencia += 1


class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO_CHOICES = [
        ('entrada', 'Entrada (Compra)'),
        ('saida', 'Saída (Venda)'),
        ('ajuste', 'Ajuste manual'),
        ('devolucao', 'Devolução'),
    ]

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='movimentacoes_estoque',
    )
    tipo_movimentacao = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO_CHOICES)
    quantidade = models.IntegerField(validators=[MinValueValidator(1)])
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_estoque',
    )
    observacao = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'gestao_movimentacaoestoque'
        ordering = ['-data_movimentacao']
        verbose_name = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'

    def __str__(self):
        return f'{self.produto.nome} - {self.get_tipo_movimentacao_display()} ({self.quantidade})'

    @property
    def quantidade_com_sinal(self):
        if self.tipo_movimentacao in {'saida', 'ajuste'}:
            return -abs(int(self.quantidade or 0))
        return abs(int(self.quantidade or 0))


class AlertaEstoque(models.Model):
    TIPO_ALERTA_CHOICES = [
        ('estoque_baixo', 'Estoque Baixo'),
        ('produto_vencido', 'Produto Vencido'),
        ('proximo_vencimento', 'Próximo ao Vencimento'),
        ('estoque_zerado', 'Estoque Zerado'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('visualizado', 'Visualizado'),
        ('resolvido', 'Resolvido'),
        ('ignorado', 'Ignorado'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo_alerta = models.CharField(max_length=30, choices=TIPO_ALERTA_CHOICES)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)
    visualizado_em = models.DateTimeField(null=True, blank=True)
    resolvido_em = models.DateTimeField(null=True, blank=True)
    resolvido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'gestao_alertaestoque'
        verbose_name = 'Alerta de Estoque'
        verbose_name_plural = 'Alertas de Estoque'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.get_tipo_alerta_display()} - {self.produto.nome}"
