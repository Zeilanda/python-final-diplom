from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User

new_user_registered = Signal(
    providing_args=['user_id'],
)


@receiver(new_user_registered)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)
    current_site = "127.0.0.1:8000"
    relativeLink = reverse('backend:user-register-confirm')
    absurl = 'http://' + current_site + relativeLink + "?token=" + str(token.key)

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


