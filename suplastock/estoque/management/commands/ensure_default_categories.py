from django.core.management.base import BaseCommand

from estoque.models import Categoria


DEFAULT_CATEGORIES = [
    "Whey Protein",
    "Termog\u00eanico",
    "Pr\u00e9-Treino",
    "Creatina",
    "BCAA",
    "Hipercal\u00f3rico",
    "Barras de Prote\u00edna",
    "Vitaminas",
    "Glutamina",
    "\u00d4mega 3",
]


class Command(BaseCommand):
    help = "Garante categorias padrao de suplementos no banco."

    def handle(self, *args, **options):
        created_count = 0
        for category_name in DEFAULT_CATEGORIES:
            _, created = Categoria.objects.get_or_create(nome=category_name)
            if created:
                created_count += 1

        total_count = Categoria.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Categorias padrao verificadas. Criadas: {created_count}. Total: {total_count}."
            )
        )
