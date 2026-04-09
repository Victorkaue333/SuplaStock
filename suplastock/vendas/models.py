# vendas/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime


class Cliente(models.Model):
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="Código único do cliente")
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    endereco = models.TextField(blank=True, null=True)
    data_cadastro = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'gestao_cliente'

    def save(self, *args, **kwargs):
        if not self.codigo:
            import uuid
            codigo_unico = str(uuid.uuid4())[:8].upper()
            self.codigo = f"CLI{codigo_unico}"
            while Cliente.objects.filter(codigo=self.codigo).exists():
                codigo_unico = str(uuid.uuid4())[:8].upper()
                self.codigo = f"CLI{codigo_unico}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nome}" if self.codigo else self.nome

    @property
    def saldo_devedor(self):
        vendas_pendentes = self.venda_set.filter(status_pagamento__in=['Pendente', 'Parcial'])
        total_devido = sum(venda.valor_pendente for venda in vendas_pendentes)
        return total_devido

    @property
    def total_compras(self):
        return self.venda_set.count()


class Venda(models.Model):
    STATUS_PAGAMENTO = [
        ('Pago', 'Pago'),
        ('Parcial', 'Parcial'),
        ('Pendente', 'Pendente'),
    ]

    produto = models.ForeignKey('estoque.Produto', on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade_vendida = models.IntegerField(validators=[MinValueValidator(1)])
    preco_venda_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    preco_original_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Preço unitário original antes de desconto",
    )
    desconto_valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor total de desconto aplicado no item da venda",
    )
    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Percentual de desconto aplicado no item da venda",
    )
    data_venda = models.DateField(auto_now_add=True)
    status_pagamento = models.CharField(max_length=20, choices=STATUS_PAGAMENTO, default='Pago')

    transacao_id = models.CharField(max_length=50, blank=True, null=True, db_index=True,
                                    help_text="ID único para agrupar produtos da mesma venda")

    cliente_nome_legado = models.CharField(max_length=255, blank=True, null=True,
                                           help_text="Nome do cliente em vendas antigas")
    forma_pagamento_legado = models.CharField(max_length=50, blank=True, null=True,
                                              help_text="Forma de pagamento em vendas antigas")

    class Meta:
        db_table = 'gestao_venda'

    def __str__(self):
        return f'Venda de {self.quantidade_vendida}x {self.produto.nome} em {self.data_venda}'

    @property
    def valor_total(self):
        return Decimal(str(self.preco_venda_unitario)) * Decimal(str(self.quantidade_vendida))

    @property
    def total_pago(self):
        pagamentos = self.pagamento_set.all()
        return sum(p.valor_pago for p in pagamentos)

    @property
    def valor_pendente(self):
        return self.valor_total - self.total_pago

    @property
    def total_venda(self):
        return self.valor_total

    @property
    def lucro(self):
        custo_total = Decimal(str(self.produto.preco_custo_unitario)) * Decimal(str(self.quantidade_vendida))
        return self.valor_total - custo_total

    def save(self, *args, **kwargs):
        if self.pk:
            if self.valor_pendente <= 0:
                self.status_pagamento = 'Pago'
            elif self.total_pago > 0:
                self.status_pagamento = 'Parcial'
            else:
                self.status_pagamento = 'Pendente'
            # Especifica explicitamente que apenas o status_pagamento deve ser atualizado
            # para evitar problemas com campos não editáveis como data_venda
            if 'update_fields' not in kwargs:
                kwargs['update_fields'] = ['status_pagamento']
        super().save(*args, **kwargs)


class Pagamento(models.Model):
    FORMAS_PAGAMENTO = [
        ('Pix', 'Pix'),
        ('Cartão de Crédito', 'Cartão de Crédito'),
        ('Cartão de Débito', 'Cartão de Débito'),
        ('Dinheiro', 'Dinheiro'),
        ('Transferência', 'Transferência'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    venda = models.ForeignKey(Venda, on_delete=models.SET_NULL, null=True, blank=True,
                              help_text="Venda específica relacionada (opcional)")
    valor_pago = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    forma_pagamento = models.CharField(max_length=50, choices=FORMAS_PAGAMENTO)
    data_pagamento = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'gestao_pagamento'
        ordering = ['-data_pagamento', '-criado_em']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'

    def __str__(self):
        return f'Pagamento de {self.cliente.nome} - R$ {self.valor_pago} em {self.data_pagamento}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.venda:
            self.venda.save()
