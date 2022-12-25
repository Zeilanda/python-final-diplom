# import yaml
# from yaml import load as load_yaml, Loader
# from django.shortcuts import render
#
# # Create your views here.
# from backend.models import Shop, Category, Product, Parameter, ProductParameter
#
# with open('orders/shop1.yaml') as stream:
#     data = load_yaml(stream, Loader=Loader)
#     try:
#         shop = Shop.objects.get_or_create(name=data['shop'])
#         for category in data['categories']:
#             category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
#             category_object.shops.add(shop.id)
#             category_object.save()
#         Product.objects.filter(shop_id=shop.id).delete()
#         for item in data['goods']:
#             product, _ = Product.objects.get_or_create(external_id=item['id'],
#                                                        name=item['name'],
#                                                        category_id=item['category'],
#                                                        model=item['model'],
#                                                        price=item['price'],
#                                                        price_rrc=item['price_rrc'],
#                                                        quantity=item['quantity'],
#                                                        shop_id=shop.id
#                                                        )
#
#             for name, value in item['parameters'].items():
#                 parameter_object, _ = Parameter.objects.get_or_create(name=name)
#                 ProductParameter.objects.create(product_id=product.id,
#                                                 parameter_id=parameter_object.id,
#                                                 value=value)
#     except yaml.YAMLError as exc:
#         print(exc)
