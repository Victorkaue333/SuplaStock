from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template


register = template.Library()


def _to_decimal(value):
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


@register.filter
def currency_br(value):
    """Formata número no padrão monetário brasileiro: R$ 70.145,00."""
    amount = _to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    is_negative = amount < 0
    amount = abs(amount)

    inteiro, decimal = f"{amount:.2f}".split(".")
    inteiro_formatado = f"{int(inteiro):,}".replace(",", ".")
    sinal = "-" if is_negative else ""
    return f"{sinal}R$ {inteiro_formatado},{decimal}"
