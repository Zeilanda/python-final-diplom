from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from backend.managers import CustomUserManager

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class User(AbstractUser):
    # username_validator = UnicodeUsernameValidator()
    email = models.EmailField(_('email address'), unique=True)

    # username = models.CharField(
    #     _('username'),
    #     max_length=150,
    #     help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    #     validators=[username_validator],
    #     error_messages={
    #         'unique': _("A user with that username already exists."),
    #     },
    # )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Customer(models.Model):
    city = models.CharField(max_length=30, verbose_name='Город', blank=True)
    street = models.CharField(max_length=30, verbose_name='Улица', blank=True)
    house = models.CharField(max_length=10, verbose_name='Дом', blank=True)
    phone = models.CharField(max_length=12, verbose_name='Телефон', blank=True)
    customer = models.ForeignKey(User, verbose_name='Клиент', related_name="user_customer", blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = "Список покупателей"
        # ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)


class Provider(models.Model):

    company = models.CharField(max_length=30, verbose_name='Компания', blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='shop_providers', blank=True,
                             on_delete=models.CASCADE)
    position = models.CharField(max_length=25, verbose_name='Должность', blank=True)
    provider = models.ForeignKey(User, verbose_name='Поставщик', related_name="user_provider", blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = "Список поставщиков"
        # ordering = ('email',)


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    model = models.CharField(max_length=50, verbose_name='Модель')
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    price = models.PositiveIntegerField()
    price_rrc = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='shop_product', blank=True,
                             on_delete=models.CASCADE)


class Parameter(models.Model):
    name = models.CharField(max_length=200)
    parameter = models.ManyToManyField(Product, through='ProductParameter')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', blank=True,
                                on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', blank=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Значение')


class Order(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='orders', blank=True,
                                 on_delete=models.CASCADE)
    status = models.CharField(max_length=15, verbose_name='Статус', choices=STATE_CHOICES)
    order_datetime = models.DateTimeField(auto_now_add=True)
    order_position = models.ManyToManyField(Product, through='OrderPosition')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"

    def __str__(self):
        return str(self.order_datetime)


class OrderPosition(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='order_positions', blank=True,
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='position_orders', blank=True,
                                on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
