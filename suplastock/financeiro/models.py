# financeiro/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from datetime import datetime


class ContaPagar(models.Model):
    CATEGORIA_CHOICES = [
        ('fornecedor', 'Fornecedor'),
        ('aluguel', 'Aluguel'),
        ('energia', 'Energia'),
        ('agua', 'Água'),
        ('internet', 'Internet'),
        ('telefone', 'Telefone'),
        ('salario', 'Salário'),
        ('impostos', 'Impostos'),
        ('marketing', 'Marketing'),
        ('manutencao', 'Manutenção'),
        ('outros', 'Outros'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]

    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    fornecedor = models.ForeignKey('estoque.Fornecedor', on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gestao_contapagar'
        verbose_name = 'Conta a Pagar'
        verbose_name_plural = 'Contas a Pagar'
        ordering = ['data_vencimento']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"

    @property
    def esta_atrasado(self):
        if self.status == 'pendente':
            return datetime.now().date() > self.data_vencimento
        return False

    def save(self, *args, **kwargs):
        if self.data_pagamento:
            self.status = 'pago'
        elif self.esta_atrasado:
            self.status = 'atrasado'
        super().save(*args, **kwargs)


class ContaReceber(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('parcial', 'Parcial'),
        ('recebido', 'Recebido'),
        ('atrasado', 'Atrasado'),
        ('cancelado', 'Cancelado'),
    ]

    ORIGEM_CHOICES = [
        ('avulsa', 'Avulsa'),
        ('fiado', 'Venda Fiada'),
    ]

    descricao = models.CharField(max_length=255)
    cliente = models.ForeignKey('vendas.Cliente', on_delete=models.CASCADE)
    venda = models.ForeignKey('vendas.Venda', on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    data_vencimento = models.DateField()
    data_recebimento = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, default='avulsa')
    transacao_id = models.CharField(max_length=50, blank=True, null=True, db_index=True,
                                    help_text="ID da transação para vincular às vendas geradas")
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True,
                                       help_text="Forma de pagamento usada no recebimento")
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gestao_contareceber'
        verbose_name = 'Conta a Receber'
        verbose_name_plural = 'Contas a Receber'
        ordering = ['data_vencimento']
        constraints = [
            models.UniqueConstraint(
                fields=['transacao_id'],
                condition=(
                    models.Q(origem='fiado', transacao_id__isnull=False)
                    & ~models.Q(transacao_id='')
                ),
                name='uniq_contareceber_transacao_fiado',
            ),
        ]

    def __str__(self):
        return f"{self.descricao} - {self.cliente.nome} - R$ {self.valor}"

    @property
    def esta_atrasado(self):
        if self.status in {'recebido', 'cancelado'}:
            return False
        return datetime.now().date() > self.data_vencimento

    @property
    def is_fiado(self):
        return self.origem == 'fiado'

    @property
    def total_recebido(self):
        total = Decimal('0')
        for recebimento in self.recebimentos.all():
            total += Decimal(str(recebimento.valor))
        return total

    @property
    def saldo_aberto(self):
        saldo = Decimal(str(self.valor)) - self.total_recebido
        return saldo if saldo > 0 else Decimal('0')

    def atualizar_status_por_recebimentos(self, *, save=True):
        """Atualiza o status com base no saldo em aberto e vencimento."""
        if self.status == 'cancelado':
            if save:
                self.save(update_fields=['status'])
            return self.status

        saldo = self.saldo_aberto
        hoje = datetime.now().date()
        total_recebido = self.total_recebido

        if saldo <= 0:
            novo_status = 'recebido'
        elif self.data_vencimento < hoje:
            novo_status = 'atrasado'
        elif total_recebido > 0:
            novo_status = 'parcial'
        else:
            novo_status = 'pendente'

        self.status = novo_status
        if novo_status == 'recebido':
            ultimo_recebimento = (
                self.recebimentos.order_by('-data_recebimento', '-criado_em').first()
            )
            if ultimo_recebimento:
                self.data_recebimento = ultimo_recebimento.data_recebimento
        elif not total_recebido:
            self.data_recebimento = None

        if save:
            self.save(update_fields=['status', 'data_recebimento'])
        return novo_status

    def save(self, *args, **kwargs):
        if self.status not in {'recebido', 'cancelado'} and self.esta_atrasado:
            self.status = 'atrasado'
        super().save(*args, **kwargs)


class ItemContaReceber(models.Model):
    """Itens individuais de uma venda fiada vinculada a uma conta a receber"""
    conta = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('estoque.Produto', on_delete=models.CASCADE)
    quantidade = models.IntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )

    class Meta:
        db_table = 'gestao_itemcontareceber'
        verbose_name = 'Item da Conta a Receber'
        verbose_name_plural = 'Itens da Conta a Receber'

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome} - R$ {self.subtotal}"

    @property
    def subtotal(self):
        return Decimal(str(self.preco_unitario)) * Decimal(str(self.quantidade))


class RecebimentoConta(models.Model):
    """Evento de recebimento vinculado a uma conta a receber."""

    FORMA_PAGAMENTO_CHOICES = [
        ('Dinheiro', 'Dinheiro'),
        ('Pix', 'Pix'),
        ('Cartão de Crédito', 'Cartão de Crédito'),
        ('Cartão de Débito', 'Cartão de Débito'),
        ('Transferência', 'Transferência'),
    ]

    conta = models.ForeignKey(
        ContaReceber,
        on_delete=models.CASCADE,
        related_name='recebimentos',
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    forma_pagamento = models.CharField(max_length=50, choices=FORMA_PAGAMENTO_CHOICES)
    data_recebimento = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recebimentos_conta_criados',
    )
    idempotency_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        help_text='Chave de idempotencia para evitar registro duplicado de recebimento.',
    )

    class Meta:
        db_table = 'gestao_recebimentoconta'
        verbose_name = 'Recebimento de Conta'
        verbose_name_plural = 'Recebimentos de Conta'
        ordering = ['-data_recebimento', '-criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['conta', 'idempotency_key'],
                condition=(
                    models.Q(idempotency_key__isnull=False)
                    & ~models.Q(idempotency_key='')
                ),
                name='uniq_recebimentoconta_conta_idempotency',
            ),
        ]

    def __str__(self):
        return f'Conta #{self.conta_id} - R$ {self.valor} em {self.data_recebimento}'


class MovimentacaoCaixa(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    CATEGORIA_CHOICES = [
        ('venda_a_vista', 'Venda à vista'),
        ('pagamento_fiado', 'Pagamento de fiado'),
        ('entrada_manual', 'Entrada manual'),
        ('despesa_operacional', 'Despesa operacional'),
        ('compra_fornecedor', 'Compra de fornecedor'),
        ('retirada', 'Retirada'),
        ('saida_manual', 'Saída manual'),
    ]

    data_movimentacao = models.DateField(default=timezone.localdate)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    origem = models.CharField(max_length=60, default='Lançamento Manual')
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_caixa_criadas',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gestao_movimentacaocaixa'
        verbose_name = 'Movimentação de Caixa'
        verbose_name_plural = 'Movimentações de Caixa'
        ordering = ['-data_movimentacao', '-criado_em', '-id']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.get_categoria_display()} - R$ {self.valor}'