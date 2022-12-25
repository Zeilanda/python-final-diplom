import yaml
from django.core.management import BaseCommand
from yaml import load as load_yaml, Loader

# Create your views here.
from backend.models import Shop, Category, Product, Parameter, ProductParameter


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # with open('fixtures/books.json', 'r', encoding='utf-8') as json_content:
        #     books = json.load(json_content)
        #
        # for book in books:
        #     Book.objects.create(name=book['fields']['name'],
        #                         author=book['fields']['author'],
        #                         pub_date=book['fields']['pub_date'])
        #         # TODO: Добавьте сохранение модели

        with open('data/shop1.yaml') as stream:
            data = load_yaml(stream, Loader=Loader)
            try:
                shop = Shop.objects.get_or_create(name=data['shop'])
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                Product.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(external_id=item['id'],
                                                               name=item['name'],
                                                               category_id=item['category'],
                                                               model=item['model'],
                                                               price=item['price'],
                                                               price_rrc=item['price_rrc'],
                                                               quantity=item['quantity'],
                                                               shop_id=shop.id
                                                               )

                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_id=product.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)
            except yaml.YAMLError as exc:
                print(exc)
