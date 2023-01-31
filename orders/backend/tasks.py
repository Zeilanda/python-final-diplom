import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from backend.models import ConfirmEmailToken
from celery import shared_task


@shared_task()
def new_user_registered(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
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
