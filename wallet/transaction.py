from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from core.notification import Notification
from .forms import TransferForm,PinForm
from .models import Wallet,Transaction as transaction_model
from .helpers import Transaction
from core.views import Messages,Email
from core.admin import AdminControls
from django.utils import timezone
from django.conf import settings
import math

import time


class CompleteTransaction(LoginRequiredMixin,UserPassesTestMixin,View) :
    """
    this handles completeing ttransaction which were incomplete for one reason or the other
    using transaction id and making sure pin matches and user is owner of transaction"""
    feedback = {}
    transaction = None
    form_class  = PinForm
    template_name = 'enter-pin.html'
    
    def get(self,request,*args,**kwargs) :
        transact = None
        if not request.user.is_activated :
            return render(request,"account_not_activated.html",locals())
        
        account = request.user.wallet
        if not account.allowed_to_transact :
            response = request.user.wallet.disallow_reason or ""
            return HttpResponse(response) 
        form =  self.form_class
        transact_id = kwargs['transact_id']
        try : 
            transact = transaction_model.objects.get(transaction_id = transact_id)        
            if transact.status == 'Successful' :
                return HttpResponse('This transaction has been processed completely')
            elif transact.status == 'Processing' :
                return HttpResponse('This transaction is already being processed,you will be notified when completed')
             
        except : return HttpResponse("Invalid request")
        if transact and not transact.transaction_type == "Internal Transfer" :
            charge = settings.INTERNATIONAL_TRANSFER_CHARGE
            charge = (charge/100) * int(transact.amount)
            charge = round(charge,2)
        else : charge = 0.00  
            
        return render(request,self.template_name,locals())



    def post(self,request,*args,**kwargs) :
        if not request.user.is_activated :
            return render(request,"account_not_activated.html",locals())
        self.feedback = {}
        form = self.form_class(request.POST)
        if form.is_valid() :
            #check pin match
            check = True #delete later
            pin = form.cleaned_data['pin']
            if not pin == request.user.wallet.transaction_pin :
                self.feedback['error'] = "The Pin You entered is incorrect,please try again !"
                return JsonResponse(self.feedback)

            if not request.user.wallet.allowed_to_transact :
                self.feedback['error'] =  request.user.wallet.disallow_reason or ""
                return JsonResponse(self.feedback) 

            transact = Transaction(request.user)
            if self.transaction.nature == 'Internal Transfer' :
                #making sure the transaction is not processed already
                if  not self.transaction.status == 'Successful' :
                    state = transact.internal_transfer(self.transaction.receiver,round(self.transaction.amount,2))
                    if  state == 0 :
        
                        msg = "Your transfer of {}{} to {},acc ******{} was successful".format(
                            self.transaction.user.wallet.currency,
                            round(self.transaction.amount,2),
                            self.transaction.receiver,
                            self.transaction.receiver.account_number[6:]
                        )
                        self.feedback['success'] = msg
                        #instantiate messages
                        #sms = Messages()
                        #SEND MESSAGE DEBIT
                        #check if user receives sms
                        #if check and  self.transaction.user.dashboard.receive_sms and self.transaction.user.phone_number_verified :
                            #sms.internal_transfer_debit_sms(self.transaction)

                        #SEND MESSAGE CREDIT
                        #check if receiver receives sms
                        #if check and  self.transaction.receiver.dashboard.receive_sms and self.transaction.receiver.phone_number_verified :
                            #sms.internal_transfer_credit_sms(self.transaction)

                        #instantiate email
                        mail = Email(send_type="alert")
                        #SEND EMAIL DEBIT
                        #check if user receives email
                        if check and self.transaction.user.email_verified :
                            mail.internal_transfer_debit_email(self.transaction)

                        #SEND MESSAGE CREDIT
                        #check if receiver receives email
                        if check and  self.transaction.receiver.dashboard.receive_email and self.transaction.receiver.email_verified :
                            mail.internal_transfer_credit_email(self.transaction)
 
                        #Notify
                        Notification.notify(request.user,msg)
                        self.transaction.status = 'Successful'
                        self.transaction.status_message = "TRF ${}  to  {},Acc ******{} ".format(
                            round(self.transaction.amount,2),
                            self.transaction.receiver,
                            self.transaction.receiver.account_number[6:]
                        )

                        self.transaction.save()
                    else :
                        self.feedback['error'] =  state 
                        return JsonResponse(self.feedback)
                else :
                    self.feedback['error'] = 'This transaction has been processed completely'
            
            else :
                #for external transfers
                if  not self.transaction.status == 'Successful' :
                    start = time.time()
                    #Check if admin gave permission for transactions
                    if not AdminControls.allow_transactions() :
                        msg = "Your transaction is been processed,you will be notified shortly"
                        self.feedback['processing'] = msg
                        self.transaction.status = "Processing"
                        self.transaction.status_message = "Your transaction is been proccessed"
                        self.transaction.save()
                        delayed  = time.time() - start
                        if  delayed < 9 :
                            time.sleep(9 - delayed)
                        return JsonResponse(self.feedback)

                    state = transact.external_transfer(round(self.transaction.amount,2))
                    if  state == 0 :
                        
                        msg = "Your transfer of {}{} to {},acc ******{} was successful".format(
                            self.transaction.user.wallet.currency,
                            round(self.transaction.amount,2),
                            self.transaction.account_name,
                            self.transaction.account_number[6:]
                        )
                        self.feedback['success'] = msg
                        #SEND MAIL
                        mail = Email(send_type='alert')
                        #check if user receives email
                        if check and  self.transaction.user.email_verified :
                            mail.external_transfer_debit_email(self.transaction)      

                        #SEND SMS
                        #sms = Messages()
                        #SEND DEBIT MESSAGE 
                        #check if user receives sms
                        #if check and  self.transaction.user.dashboard.receive_sms and self.transaction.user.phone_number_verified :
                            #sms.external_transfer_debit_sms(self.transaction)      

                        #NOTIFY
                        Notification.notify(request.user,msg)
                        self.transaction.status = 'Successful'
                        self.transaction.status_message = "TRF ${}  to  {},Acc ******{} ".format(
                            round(self.transaction.amount,2),
                            self.transaction.account_name,
                            self.transaction.account_number[6:]
                        )
                        self.transaction.save()
                        delayed  = time.time() - start
                        if  delayed < 7 :
                            time.sleep(7 - delayed)

                    else :
                        self.feedback['error'] =  state 
                        return JsonResponse(self.feedback)

                elif self.transaction.status == 'pending' :  
                    self.feedback['error'] = "this Transaction is already pending,you will be notified when its completed"      
                else :  
                    self.feedback['error'] = 'This transaction has been processed completely'
                return JsonResponse(self.feedback)

             



        else :
            err = getattr(form,'pin')
            self.feedback['error'] = err.errors

            return JsonResponse(self.feedback) 
            
        return JsonResponse(self.feedback)          

    def test_func(self) :
        transact_id = self.kwargs['transact_id']
        try : transaction = transaction_model.objects.get(transaction_id = transact_id)        
        except : return False
        #THE TRANSACTION OBJECT
        self.transaction = transaction
        return transaction.user == self.request.user



class Transfer(LoginRequiredMixin,View) :

    template_name = 'transfer.html'
    form_class = TransferForm
    model2 = Wallet 
    model = get_user_model


    def get(self,request,*args,**kwargs) :
        
        account = request.user.wallet
        form =  self.form_class
        return render(request,self.template_name,locals())


    def post(self,request,*args,**kwargs) :
        start = time.time()
        form = self.form_class(
            user=self.request.user,
            data=request.POST
            ) 

        if form.is_valid() :
            error = None
            acc_num = form.cleaned_data.get('account_number') 
            amount = form.cleaned_data.get('amount')
            transact_type = form.cleaned_data.get('transfer_type')
            #if internal
            receipient = None
            if  transact_type == 'Internal Transfer' :
                charge = 0.00
                receipient = get_user_model().objects.get(account_number = acc_num)
            

            else :
                max_charge = 50
                charge_due_amount = 0.08 * amount 
                charge = max_charge if max_charge < charge_due_amount else charge_due_amount
                iban = form.cleaned_data.get('iban')
                bic = form.cleaned_data.get('bic')
                swift_number = form.cleaned_data.get('swift_number')
                #check if details is in our list,else give network error
                error = None
                  
             
            
            #check if user has the amount
            if request.user.wallet.available_balance < float(amount + charge) :
                error = "Insufficient Funds,Enter a lower amount"
                return render(request,self.template_name,locals())
     
        
            acc_name,bank_name,country = None,None,None

            transact = transaction_model.objects.create(
                user = request.user,
                amount = amount,
                transaction_type = 'Debit',
                nature = form.cleaned_data['transfer_type'],
                description = form.cleaned_data['description'],
                charge = charge,
                status = "pending",
                status_message  = "Waiting for Transaction Pin Authorization",
                receiver  = receipient,
                swift_number = form.cleaned_data.get('swift_number',None),
                iban =  form.cleaned_data.get('iban',None),
                bic =  form.cleaned_data.get('bic',None),
                account_number =  acc_num,
                account_name = acc_name,
                country = country,
                bank_name = bank_name
            )
            return HttpResponseRedirect(reverse('complete-transaction',args=[transact.transaction_id]))    
        else :
            return render(request,self.template_name,locals())     
            




