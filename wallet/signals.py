from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from .models import Transaction
from core.communication import TransactionMail
from core.notification import Notification


@receiver(post_save, sender=Transaction)
def send_mail(sender, instance, created, **kwargs):
    if instance.status == "successful" and not instance.mail_is_sent :
        # SEND MAIL
        mail = TransactionMail(instance)
        mail.send_transaction_mail()
        instance.mail_is_sent = True
        instance.save()
        # SEND SMS
        #sms = Messages()
        # sms.send_transaction_sms(self.transaction)
        # NOTIFY
        #Notification.transaction_notification(instance)