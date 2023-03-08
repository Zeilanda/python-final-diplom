import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from backend.models import ConfirmEmailToken, ConfirmOrderToken
from celery import shared_task


@shared_task()
def new_user_registered(user_id, **kwargs):
    """
    Отправляем письмо с подтверждением почты
    """
    logging.warning('Registered start')
    print('Registered start!!!')
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


@shared_task()
def new_order_created(order_id, address, **kwargs):
    """
    Отправляем письмо с подтверждением заказа
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
