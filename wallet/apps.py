from django.apps import AppConfig
from django.core.signals import request_finished


class WalletConfig(AppConfig):
    name = 'wallet'

    def ready(self) :
        from . import signals
        from .models import Transaction
        request_finished.connect(signals.send_mail, sender=Transaction)    


