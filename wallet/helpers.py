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
    def __init__(self,transaction) :
        self.transaction = transaction

    

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


           





