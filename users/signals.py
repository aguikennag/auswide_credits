
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db.models import Q
from django.conf import settings

from wallet.models import Wallet
from users.models import Dashboard
from core.communication import AccountMail


@receiver(post_save, sender=get_user_model())
def create_user_credentials(sender, instance, created, **kwargs):
    if  created :
        Dashboard.objects.create(user = instance)
        #send registration email
        mail = AccountMail(instance)
        mail.send_registration_email()
