from django.db import models
from django.contrib.auth import get_user_model
from core.notification import Notification
from core.views import Email
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
import random
import time


class Currency(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return self.symbol


class Wallet(models.Model):

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='wallet')
    transaction_pin = models.CharField(
        max_length=6, null=False, default="0000")
    otp = models.CharField(max_length=8, blank=True, null=True)
    currency = models.ForeignKey(
        Currency, related_name='wallets', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super(Wallet, self).save(*args, **kwargs)

    @property
    def ledger_balance(self):
        credits = self.user.transaction.filter(
            transaction_type="credit",
            status="successful"
        ).aggregate(
            credits=Sum("amount")
        )['credits'] or 0.00

        debits = self.user.transaction.filter(
            transaction_type="debit",
            status="successful"
        ).aggregate(
            debits=Sum("amount")
        )['debits'] or 0.00

        return credits - debits

    @property
    def available_balance(self):
        return self.ledger_balance


class Transaction(models.Model):
    try:
        international_charge = settings.INTERNATIONAL_TRANSFER_CHARGE
        internal_charge = settings.INTERNAL_TRANSFER_CHARGE
    except:
        international_charge = 2
        internal_charge = 0.5

    def get_transaction_id(self):
        PREFIX = "ZF"
        number = random.randrange(10000000000, 9999999999999999999)
        number = PREFIX + str(number)
        if Transaction.objects.filter(transaction_id=number).exists():
            self.get_transaction_id()
        return number

    TRANSACTION_TYPE = (('debit', 'debit'), ('credit', 'credit'))
    TRANSACTION_NATURE = (('Withdrawal', 'Withdrawal'),
                          ('Deposit', 'Deposit'),
                          ('Internal Transfer', 'Internal Transfer'),
                          ('Domestic Transfer', 'Domestic Transfer'),
                          ('International Transfer', 'International Transfer'))

    STATUS = (('failed', 'failed'),
              ('pending', 'pending'),
              ('srocessing', 'Processing'),
              ('successful', "successful"))

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='transaction')
    transaction_id = models.CharField(
        editable=False, unique=True, null=False, max_length=20)
    amount = models.FloatField()
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE, max_length=10)
    nature = models.CharField(
        choices=TRANSACTION_NATURE, max_length=32, null=False, blank=False)
    status = models.CharField(choices=STATUS, max_length=10)
    description = models.TextField(null=True, blank=False)

    # if transfer,can be blank for international transfer
    receiver = models.ForeignKey(get_user_model(
    ), related_name='transfer_receiver', on_delete=models.CASCADE, null=True, blank=True)
    status_message = models.TextField()
    charge = models.FloatField(blank=True, default=0.0, null=False)

    # for international transfer
    iban = models.CharField(max_length=40, blank=True, null=True)
    bic = models.CharField(max_length=40, blank=True, null=True)
    swift_number = models.CharField(max_length=30, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_name = models.CharField(max_length=40, blank=True, null=True)
    bank_name = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)

    # for controlling transactions
    is_approved = models.BooleanField(default=False)
    date_approved = models.DateTimeField(null=True, blank=True)
    is_failed = models.BooleanField(default=False)
    failure_reason = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    new_date = models.DateTimeField(null=True, blank=True)

    def fulfill(self):
        """
        fulfilling transaction upon transaction pin verification
        """
        if self.status == "successful":
            return {"error": "this transaction has already been completed"}

        elif self.status == 'processing':
            return {"error" : "this Transaction is already pending, you will be notified when its completed"}

        elif self.status == "failed" :
            return {"error" : 'You cannot process this transaction, please contact support.'}

        msg = "Your transfer of {}{} to {},acc ******{} was successful".format(
            self.user.wallet.currency,
            round(self.amount, 2),
            self.receiver,
            self.receiver.account_number[6:]
        )

        # update a transaction
        self.status = "successful"
        self.status_message = "TRF ${}  to  {},Acc ******{} ".format(
            round(self.amount, 2),
            self.receiver,
            self.receiver.account_number[6:]
        )
        self.save()
        if self.nature == "Internal Transfer":
            pass

        else:
            start = time.time()
            delayed = time.time() - start
            if delayed < 7:
                time.sleep(7 - delayed)

        return {'success': msg}

    def save(self, *args, **kwargs):
        if self.is_approved and not self.status == "Successful" and self.nature and not self.date_approved == "International Transfer":
            self.date_approved = timezone.now()
            # initiate email sending
            from .helpers import Transaction as Transact
            transact = Transact(self.user)
            transact.handle_approved_transactions(self)
        # if self.nature = "International Transfer" : is_approved = True
        if not self.transaction_id:
            self.transaction_id = self.get_transaction_id()

        if self.status == 'Failed':
            # notify user
            # email user
            # sms user
            pass
        self.amount = round(self.amount, 2)

        if not self.new_date:
            self.new_date = self.date
        if self.transaction_type == "Internal Transfer":
            self.charge = settings.INTERNATIONAL_TRANSFER_CHARGE
            self.charge = (charge/100) * int(self.amount)
            self.charge = round(charge, 2)

        else:
            charge = 0.00
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return self.transaction_id

    @property
    def show_date(self):
        if self.new_date:
            return self.new_date
        else:
            return self.date

    class Meta():
        ordering = ['-new_date', '-date']
