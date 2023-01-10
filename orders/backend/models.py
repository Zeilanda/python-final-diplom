from datetime import datetime, timedelta
import jwt
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


# class UserManager(BaseUserManager):
#     """
#     Django требует, чтобы пользовательские `User`
#     определяли свой собственный класс Manager.
#     Унаследовав от BaseUserManager, мы получаем много кода,
#     используемого Django для создания `User`.
#
#     Все, что нам нужно сделать, это переопределить функцию
#     `create_user`, которую мы будем использовать
#     для создания объектов `User`.
#     """
#
#     def _create_user(self, username, email, password=None, **extra_fields):
#         if not username:
#             raise ValueError('Указанное имя пользователя должно быть установлено')
#
#         if not email:
#             raise ValueError('Данный адрес электронной почты должен быть установлен')
#
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#
#         return user
#
#     def create_user(self, username, email, password=None, **extra_fields):
#         """
#         Создает и возвращает `User` с адресом электронной почты,
#         именем пользователя и паролем.
#         """
#         extra_fields.setdefault('is_staff', False)
#         extra_fields.setdefault('is_superuser', False)
#
#         return self._create_user(username, email, password, **extra_fields)
#
#     def create_superuser(self, username, email, password, **extra_fields):
#         """
#         Создает и возвращает пользователя с правами
#         суперпользователя (администратора).
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Суперпользователь должен иметь is_staff=True.')
#
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Суперпользователь должен иметь is_superuser=True.')
#
#         return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    is_provider = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Сообщает Django, что класс UserManager, определенный выше,
    # должен управлять объектами этого типа.
    # objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def token(self):
        """
        Позволяет нам получить токен пользователя, вызвав `user.token` вместо
        `user.generate_jwt_token().

        Декоратор `@property` выше делает это возможным.
        `token` называется «динамическим свойством ».
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        Этот метод требуется Django для таких вещей,
        как обработка электронной почты.
        Обычно это имя и фамилия пользователя.
        Поскольку мы не храним настоящее имя пользователя,
        мы возвращаем его имя пользователя.
        """
        return self.username

    def get_short_name(self):
        """
        Этот метод требуется Django для таких вещей,
        как обработка электронной почты.
        Как правило, это будет имя пользователя.
        Поскольку мы не храним настоящее имя пользователя,
        мы возвращаем его имя пользователя.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Создает веб-токен JSON, в котором хранится идентификатор
        этого пользователя и срок его действия
        составляет 60 дней в будущем.
        """
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': self.pk,
            'exp': int(round(dt.timestamp()))
        }, settings.SECRET_KEY, algorithm='HS256')


        # return token.decode('utf-8')
        # return jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        return token


class Customer(models.Model):
    city = models.CharField(max_length=30, verbose_name='Город', blank=True)
    street = models.CharField(max_length=30, verbose_name='Улица', blank=True)
    house = models.CharField(max_length=10, verbose_name='Дом', blank=True)
    phone = models.CharField(max_length=12, verbose_name='Телефон', blank=True)
    customer = models.OneToOneField(User, verbose_name='Клиент', related_name="user_customer", blank=True,
                                    on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = "Список покупателей"
        # ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название', unique=True)
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)


class Provider(models.Model):
    company = models.CharField(max_length=30, verbose_name='Компания', blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='shop_providers', blank=True,
                             on_delete=models.CASCADE)
    position = models.CharField(max_length=25, verbose_name='Должность', blank=True)
    provider = models.OneToOneField(User, verbose_name='Поставщик', related_name="user_provider", blank=True,
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
