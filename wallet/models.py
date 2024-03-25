from django.urls import reverse
from django.db import models
from django.contrib.auth import get_user_model
from core.notification import Notification
from core.communication import TransactionMail
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from django.forms.models import model_to_dict
from core.helpers import custom_model_to_dict
import random
import time


class Currency(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5)
    symbol = models.CharField(max_length=5)

    def __str__(self):
        return "{}({})".format(self.symbol,self.code)


class DemoAccountDetails(models.Model) :
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=50)
    iban = models.CharField(max_length=50)
    swift_number  = models.CharField(max_length=50)
    bank_name  = models.CharField(max_length=50)
    country  = models.CharField(max_length=50)

    def __str__(self) :
        return self.account_name


class Wallet(models.Model):

    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='wallet')
    savings = models.DecimalField(decimal_places=2,max_digits=50,default=0.00)    
    bills = models.DecimalField(decimal_places=2,max_digits=50,default=0.00)   
    transaction_pin = models.CharField(
        max_length=6, null=False, default="0000")
    otp = models.CharField(max_length=8, blank=True, null=True)
    currency = models.ForeignKey(
        Currency, related_name='wallets', on_delete=models.CASCADE, null=False)
    
     #control spot
    allowed_to_transact = models.BooleanField(default=True)
    #when user is disaaalowed from makimg transactions
    disallow_reason = models.TextField(null = False,blank = True)
    is_frozen  = models.BooleanField(default = False)


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super(Wallet, self).save(*args, **kwargs)


    @property
    def income(self) :
        return self.user.transaction.filter(
            transaction_type="credit",
            status="successful"
        ).aggregate(
            credits=Sum("amount")
        )['credits'] or 0.00
    
    @property
    def expense(self) :
        return  self.user.transaction.filter(
            transaction_type="debit",
            status="successful"
        ).aggregate(
            debits=Sum("amount")
        )['debits'] or 0.00



    @property
    def ledger_balance(self):
        return self.income - self.expense

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
        PREFIX = "OPG"
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
                          ('International Transfer', 'International Transfer'),
                          ('Bonus', 'Bonus'))

    STATUS = (('failed', 'failed'),
              ('pending', 'pending'),
              ('processing', 'Processing'),
              ('successful', "successful"))

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                             related_name='transaction')
    transaction_id = models.CharField(
        editable=False, unique=True, null=False, max_length=20)
    amount = models.FloatField(default=0.00)
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE, max_length=10)
    nature = models.CharField(
        choices=TRANSACTION_NATURE, max_length=32, null=False, blank=False)
    status = models.CharField(choices=STATUS, max_length=10,default="failed",null =False)
    description = models.TextField(null=True, blank=False)

    # if transfer,can be blank for international transfer
    receiver = models.ForeignKey(get_user_model(
    ), related_name='transfer_receiver', on_delete=models.CASCADE, null=True, blank=True)
    status_message = models.TextField(blank = True, null = True)
    charge = models.FloatField(blank=True, default=0.0, null=False)

    # for international transfer
    iban = models.CharField(max_length=40, blank=True, null=True)
    bic = models.CharField(max_length=40, blank=True, null=True)
    swift_number = models.CharField(max_length=30, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    account_name = models.CharField(max_length=40, blank=True, null=True)
    bank_name = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)
    new_date = models.DateTimeField(null=True, blank=True)
    mail_is_sent = models.BooleanField(default = False)

    def as_dict(self) :
        dict_vals =  dict((field.name, getattr(self, field.name)) for field in self._meta.fields)
        return dict_vals


    def fulfill(self):
        """
        fulfilling transaction upon transaction pin verification,
        create new transaction for credits and debits and delethis this one
        """
        if self.status == "successful":
            return {"error": "this transaction has already been completed"}

        elif self.status == 'processing':
            return {"error": "this Transaction is already pending, you will be notified when its completed"}

        elif self.status == "failed":
            return {"error": 'You cannot process this transaction, please contact support.'}


        if self.nature == "Internal Transfer":
            # create for credit
            data = self.as_dict()
        
            del data['transaction_id'] #maintain unique values
            if data.get("id") : del data['id']
            credit_trx = Transaction(
               **data
            )
            credit_trx.status = "successful"
            credit_trx.transaction_type = "credit"
            credit_trx.user = self.receiver
            credit_trx.save()
           

            # create for debit
            debit_trx = Transaction(
                **data
            )
            debit_trx.transaction_type = "debit"
            debit_trx.status = "successful"
            debit_trx.save()
            
            # delete this transaction
            self.delete()  

        else:
            # testing network delay effect
            start = time.time()
            delayed = time.time() - start
            if delayed < 5:
                time.sleep(5 - delayed)
            self.status_message = "transaction completed"
            self.status = "successful"
            self.save()

        feedback_msg = "Your transfer  of {}{} was successful".format(self.user.wallet.currency,self.amount)
        
        return { 'success': feedback_msg , 'success_url' : reverse("dashboard")}


    def save(self, *args, **kwargs):

        if not self.transaction_id:
            self.transaction_id = self.get_transaction_id()

        if self.amount :
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
