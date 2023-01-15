from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User, ConfirmOrderToken

new_user_registered = Signal(
    providing_args=['user_id'],
)

new_order = Signal(
    providing_args=['order_id', "address"]
)


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    current_site = "127.0.0.1:8000"
    relative_link = reverse('backend:user-register-confirm')
    absurl = 'http://' + current_site + relative_link + "?token=" + str(token.key)

    msg = EmailMultiAlternatives(
        # title:
        "Verify your email",
        # message:
        f"Hi, {token.user.first_name}, this is the resent link to verify your email: {absurl}",
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    print("verify url:", absurl)
    msg.send()
    print("new_user_registered_signal")


@receiver(new_order)
def new_order_created_signal(order_id, address, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmOrderToken.objects.get_or_create(order_id=order_id, address=address)
    current_site = "127.0.0.1:8000"
    relative_link = reverse('backend:order-confirm')
    absurl = 'http://' + current_site + relative_link + "?token=" + str(token.key)

    msg = EmailMultiAlternatives(
        # title:
        "Verify your order",
        # message:
        f"Hi, {token.order.user.user.first_name} this is the resent link to verify your order: "
        f"{absurl} to the address: {address}",
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.order.user.user.email]
    )
    print("verify url:", absurl)
    msg.send()
