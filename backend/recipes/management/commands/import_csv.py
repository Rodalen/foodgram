import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            with open('ingredients.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    Ingredient.objects.get_or_create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
            print('Ингредиенты загружены.')
        except Exception as error:
            print(f'Ошибка при загрузке ингредиентов: {error}')
