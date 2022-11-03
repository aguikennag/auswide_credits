from core.notification import Notification
from core.views import Email
import datetime
import time
from django.utils import timezone
from django.conf import settings
#from djmoney.money import 
from .models import Transaction as transaction_model
from core.views import Email
from core.helpers import Helper

class Transaction() :
    def __init__(self,user) :
        self.user = user


    def credit(self,amount,user=None)  :
        if not user : user = self.user
        wallet = user.wallet
        wallet.available_balance += amount 
        wallet.save()
        #ensure it added
        return
            

    def debit(self,amount,user=None) :
        
        if not user : user = self.user
        wallet = user.wallet
        wallet.available_balance -= amount
        wallet.save()
        #ensure it added
        return

    def external_transfer(self,amount) : 
        charge = settings.INTERNATIONAL_TRANSFER_CHARGE
        charge = (charge/100) * amount
        try :
            self.debit(amount + charge)
            state = 0
        except :
            state =  "An Error occured"    
        return state

    def internal_transfer(self,receiver,amount) : 
        """
        currency is the receiving account currency"""
        #convert to receiver currency
        _from = self.user.wallet.currency
        _to = receiver.wallet.currency
        converted_amount = Helper.currency_convert(amount,_from,_to)
        try :
            self.debit(amount)
            self.credit(converted_amount,receiver)
            state = 0
        except :
            state =  "An Error occured"    
        return state  


    def handle_approved_transactions(self,transaction) :
        transact = Transaction(transaction.user)
        state = transact.external_transfer(transaction.amount)
        if  state == 0 and transaction.user.dashboard.receive_email and transaction.user.email_verified :
            mail = Email(send_type='alert')
            mail.external_transfer_debit_email(transaction)
            msg = "Your transfer of {}{} to {},iban ******{} was successful".format(
                transaction.user.wallet.currency,
                transaction.amount,
                transaction.account_name,
                transaction.iban[6:]
            )
            Notification.notify(transaction.user,msg)
            transaction.status = 'Successful'
            transaction.status_message = "TRF {}{}  to  {},iban ******{} ".format(
            transaction.user.wallet.currency,
            transaction.amount,
            transaction.account_name,
            transaction.iban[6:]
            )
            transaction.save()


        
           





