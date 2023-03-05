from datetime import datetime, timedelta
import jwt
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_rest_passwordreset.tokens import get_token_generator

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Класс User, наследуется от AbstractUser
    """
    is_provider = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    #
    # @property
    # def token(self):
    #     """
    #     Позволяет нам получить токен пользователя, вызвав `user.token` вместо
    #     `user.generate_jwt_token().
    #
    #     Декоратор `@property` выше делает это возможным.
    #     `token` называется «динамическим свойством ».
    #     """
    #     return self._generate_jwt_token()
    #
    # def get_full_name(self):
    #     """
    #     Этот метод требуется Django для таких вещей,
    #     как обработка электронной почты.
    #     Обычно это имя и фамилия пользователя.
    #     Поскольку мы не храним настоящее имя пользователя,
    #     мы возвращаем его имя пользователя.
    #     """
    #     return self.username
    #
    # def get_short_name(self):
    #     """
    #     Этот метод требуется Django для таких вещей,
    #     как обработка электронной почты.
    #     Как правило, это будет имя пользователя.
    #     Поскольку мы не храним настоящее имя пользователя,
    #     мы возвращаем его имя пользователя.
    #     """
    #     return self.username
    #
    # def _generate_jwt_token(self):
    #     """
    #     Создает веб-токен JSON, в котором хранится идентификатор
    #     этого пользователя и срок его действия
    #     составляет 60 дней в будущем.
    #     """
    #     dt = datetime.now() + timedelta(days=60)
    #     token = jwt.encode({
    #         'id': self.pk,
    #         'exp': int(round(dt.timestamp()))
    #     }, settings.SECRET_KEY, algorithm='HS256')
    #
    #     # return token.decode('utf-8')
    #     # return jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
    #     return token


class Customer(models.Model):
    """
    Класс для покупателя (клиента)
    """
    city = models.CharField(max_length=30, verbose_name='Город', blank=True)
    street = models.CharField(max_length=30, verbose_name='Улица', blank=True)
    house = models.CharField(max_length=10, verbose_name='Дом', blank=True)
    phone = models.CharField(max_length=12, verbose_name='Телефон', blank=True)
    user = models.OneToOneField(User, verbose_name='Клиент', related_name="user_customer", blank=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = "Список покупателей"
        # ordering = ('email',)


class Shop(models.Model):
    """
    Класс для магазина
    """
    name = models.CharField(max_length=50, verbose_name='Название', unique=True)
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)


class Provider(models.Model):
    """
    Класс для поставщика
    """
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
    """
    Класс для категорий товаров
    """
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Класс для товаров
    """
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

    def __str__(self):
        return self.name


class Parameter(models.Model):
    """
    Класс для параметров товаров
    """
    name = models.CharField(max_length=200)
    parameter = models.ManyToManyField(Product, through='ProductParameter')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """
    Класс для связывания товаров и их параметров
    """
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='parameters', blank=True,
                                on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', blank=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Значение')


class Order(models.Model):
    """
    Класс для заказов
    """
    user = models.ForeignKey(Customer, to_field="user_id", verbose_name='Покупатель', related_name='orders',
                             blank=True,
                             on_delete=models.CASCADE)
    status = models.CharField(max_length=15, verbose_name='Статус', choices=STATE_CHOICES)
    order_datetime = models.DateTimeField(auto_now_add=True)
    address = models.TextField(verbose_name='Адрес', null=True)

    # order_position = models.ManyToManyField(Product, through='OrderPosition')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"

    def __str__(self):
        return str(self.order_datetime)


class OrderPosition(models.Model):
    """
    Класс для связи заказов и товаров
    """
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='positions', blank=True, null=True,
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='order_positions', blank=True,
                                on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product'], name='unique_order_item'),
        ]


class ConfirmEmailToken(models.Model):
    """
    Класс для подтверждения своего аккаунта пользователем
    """
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this email confirmation")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Email confirmation token for user {user}".format(user=self.user)


class ConfirmOrderToken(models.Model):
    """
    Класс для подтверждения своего заказа покупателем
    """
    class Meta:
        verbose_name = 'Токен подтверждения заказа'
        verbose_name_plural = 'Токены подтверждения заказа'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    order = models.ForeignKey(
        Order,
        related_name='confirm_order_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The Order which is associated to this confirmation")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )
    address = models.TextField()
    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Confirmation token for order {self.order}"
