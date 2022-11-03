from django.shortcuts import render
from django.views.generic import RedirectView,View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string,get_template
from django.conf import settings
from django.utils import timezone
from core.helpers import Helper
#import imgkit
from io import BytesIO
#from  xhtml2pdf import pisa
import random
from twilio.rest import Client


class ValidationCode()     :
    @staticmethod
    def generate_code(user,email=None,phone_number=None,offset = None,send_type = 'message') :
        """ offset is the active time for the code,
        """
        offset = offset or 5
        expiry = timezone.now() + timezone.timedelta(minutes=offset)
        code = random.randrange(99999,999999)
        db = user.dashboard
        db.otc = int(code)
        db.otc_expiry = expiry
        db.save()
        ctx = {'expiry' : expiry.time(),'code' : code}
        email_receiver = user.email
        #payload = self.convert_html_to_pdf(template_name,ctx)
        name = user.name or user.username
        
      
        
        if send_type == 'message' :
            msg = "credo finance bank phone number verification code is {}".format(code)
            sms = Messages()
            sms.send_sms(phone_number,msg)


        elif send_type == 'email' :
            subject = "Credo Finance email verification"
            mail = Email(send_type='support')
            ctx['name'] = name
            mail.send_html_email([email_receiver],subject,"otp-email.html",ctx=ctx)


    @staticmethod
    def validate_otc(user,code) :
        """
        returns a tuple of the validations state and error  if theres any or None as 2nd index
        """
        if user.dashboard.otc == int(code) :
            if not timezone.now() < user.dashboard.otc_expiry :
                error = "The entered code is correct,but has expired"
                return (False,error)
            else : 
                return (True,None)  

        else :
            return (False,"The entered code is incorrect")  

        return (False,"unknown error occured")           






class Email() :
    def __init__(self,send_type = "support") :
        from django.core.mail import get_connection
        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT    
        senders = {
            'alert' : settings.EMAIL_HOST_USER_ALERT,
            'support' : settings.EMAIL_HOST_USER_SUPPORT
            }
        if not send_type :
           self.send_from = senders['alert']
        else :
            self.send_from = senders.get(send_type,senders['alert'])
        self.auth_connecion = get_connection(
            host = host,
            port = port,
            username = self.send_from,
            password = settings.EMAIL_HOST_PASSWORD ,
            use_tls = settings.EMAIL_USE_TLS
        ) 


    def convert_html_to_pdf(self,html_template,ctx=None) :
        """ converts a html template to pdf and returns the new pdf"""
        template = get_template(html_template)
        html = template.render(ctx)
        results = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),results)
        if not pdf.err :
            return results.getvalue()
        return None

 



    def send_email(self,receive_email_list,subject,message,headers=None) :
        headers = {
            'Content-Type' : 'text/plain'
        } 
        try : 
            email = EmailMessage(subject = subject,body=message,
            from_email=self.send_from,to=receive_email_list,
            headers = headers,connection=self.auth_connecion)
            email.send()
            self.auth_connecion.close()
        except :
            pass

    def send_html_email(self,receive_email_list,subject,template,ctx=None) :
        msg = render_to_string(template,ctx)
        email = EmailMessage(subject,msg,self.send_from,receive_email_list,connection=self.auth_connecion)
        email.content_subtype = "html"
        #try :
        email.send()
        #except : pass    
        self.auth_connecion.close()
    
        


    def send_file_email(self,file_name,_file,receive_email_list,subject,message) :
        email = EmailMessage(subject,message,self.send_from,receive_email_list,connection=self.auth_connecion)
        email.attach(file_name,_file)
        try : 
            email.send()
            self.auth_connecion.close()
        except : pass

    

    def internal_transfer_debit_email(self,transaction) :
        
        acc_num = "{}***..*{}{}".format(
        transaction.user.account_number[0],
        transaction.user.account_number[-2],
        transaction.user.account_number[-1]
        )
        msg="Internal transfer to {}.DESC : {}".format(transaction.receiver,transaction.description)
        ctx = {
            'acc_num' : acc_num,
            'acc_name' : transaction.user,
            'amount' : "{}{}".format(transaction.user.wallet.currency,transaction.amount),
    
            'balance' : "{}{}".format(transaction.user.wallet.currency,transaction.user.wallet.available_balance),
            'msg' : msg,
            'trasnaction_id' : transaction.transaction_id,
            'trasnaction_type' : transaction.transaction_type,
            'date' : transaction.date
        }   
        subject = "Credo Finance Bank Transaction Alert" 
        email_receiver = transaction.user.email
        name = transaction.user.name or transaction.user.username
        
        ctx['name'] = name
        self.send_html_email([email_receiver],subject,"transaction-email.html",ctx=ctx)
        

    def internal_transfer_credit_email(self,transaction) :
        amt = transaction.receiver.wallet.currency,transaction.amount
        _from = transaction.user.wallet.currency
        _to = transaction.receiver.wallet.currency
        converted_amount = Helper.currency_convert(amt,_from,_to)
        acc_num = "{}***..*{}{}".format(
        transaction.user.account_number[0],
        transaction.user.account_number[-2],
        transaction.user.account_number[-1]
        )
        msg="Received funds from {}.DESC : {}".format(transaction.receiver,transaction.description)
        ctx = {
            'acc_num' : acc_num,
            'acc_name' : transaction.receiver,
            'amount' : "{}{}".format(_to,converted_amount),
            'balance' : "{}{}".format(transaction.receiver.wallet.currency,transaction.receiver.wallet.available_balance),
            'msg' : msg,
            'trasnaction_id' : transaction.transaction_id,
            'trasnaction_type' : transaction.transaction_type,
            'date' : transaction.date
        }    
        email_receiver = transaction.receiver.email
        #payload = self.convert_html_to_pdf(template_name,ctx)
        subject = "Credo Finance Bank Transaction Alert"
        try : name = transaction.receiver.first_name + transaction.receiver.last_name
        except : transaction.receiver.username
        ctx['name'] = name
        self.send_html_email([email_receiver],subject,"transaction-email.html",ctx=ctx)

        """msg = "Hello {},there has been  a recent transaction activity on your {} account,contained in this pdf are the details of  that transaction.".format(nam,transaction.receiver.account_type)
        self.send_file_email('transaction_alert.pdf',payload,[email_receiver],subject,msg)"""

  
    def external_transfer_debit_email(self,transaction) :

        receipient_str =  "{},iban - {},bank - {}".format(transaction.account_name,
        transaction.iban,
        transaction.bank_name)
        
        acc_num = "{}*****..*{}{}".format(
        transaction.user.account_number[0],
        transaction.user.account_number[-2],
        transaction.user.account_number[-1]
        )
        msg="international transfer to {}.DESC : {}".format(receipient_str,transaction.description)
        ctx = {
            'acc_num' : acc_num,
            'acc_name' : transaction.user,
            'amount' : "{}{}".format(transaction.user.wallet.currency,transaction.amount),
            'balance' : "{}{}".format(transaction.user.wallet.currency,transaction.user.wallet.available_balance),
            'msg' : msg,
            'transaction_id' : transaction.transaction_id,
            'transaction_type' : transaction.transaction_type,
            'date' : transaction.date
        }    
        email_receiver = transaction.user.email
        #payload = self.convert_html_to_pdf(template_name,ctx)
        #name = transaction.receiver.name or transaction.receiver.username
        subject = "Credo Finance Bank Transaction Alert"
       
        ctx['name'] = transaction.user
        self.send_html_email([email_receiver],subject,"transaction-email.html",ctx=ctx)
            
 
class Messages() :

    def __init__(self) :
        self.client = Client(settings.TWILLO_ACCOUNT_SID,settings.TWILLO_AUTH_TOKEN)
    

    def send_sms(self,phone_number,message) :
        try :
            message = str(message)
            phone_number = str(phone_number)
            if not phone_number.startswith('+') : 
                raise ValueError("Phone number must be in international format")
        except : 
            raise ValueError("message and phone number must be in string format")    
        try :
            self.client.messages.create(
                to = phone_number,
                from_= settings.SMS_PHONE_NUMBER,
                body = message
                )
        except : pass
                    


    def internal_transfer_debit_sms(self,transaction) :
        acc_number = "{}***..*{}{}".format(
            transaction.user.account_number[0],
            transaction.user.account_number[-2],
            transaction.user.account_number[-1]
            )
        msg = """
        Txn : Debit\n
        Acc : {}\n
        Amt : {}\n
        Desc : Internal Transfer to {},{}\n
        Bal : {}\n
        Date  : {}""".format(acc_number,
        transaction.amount,
        transaction.user,
        transaction.user.account_number,
        transaction.user.wallet.available_balance,
        timezone.now()
        )
        self.send_sms(transaction.user.phone_number,msg)


    def internal_transfer_credit_sms(self,transaction) :
        acc_number = "{}***..*{}{}".format(
            transaction.receiver.account_number[0],
            transaction.receiver.account_number[-2],
            transaction.receiver.account_number[-1]
            )

        msg = """
        Txn : Credit\n
        Acc : {}\n
        Amt : {}\n
        Desc : Received funds from {},{}\n
        Bal : {}\n
        Date  : {}""".format(acc_number,
        transaction.amount,
        transaction.receiver,
        transaction.receiver.account_number,
        transaction.receiver.wallet.available_balance,
        timezone.now()
        )
        self.send_sms(transaction.receiver.phone_number,msg) 

    
    def external_transfer_debit_sms(self,transaction) :
        acc_number = "{}***..*{}{}".format(
            transaction.user.account_number[0],
            transaction.user.account_number[-2],
            transaction.user.account_number[-1]
            )
        msg = """
        Txn : Debit\n
        Acc : {}\n
        Amt : {}\n
        Desc : International Transfer to {},iban - {},bank - {}\n
        Bal : {}\n
        Date  : {}""".format(acc_number,
        transaction.amount,
        transaction.account_name,
        transaction.iban,
        transaction.bank_name,
        transaction.user.wallet.available_balance,
        timezone.now()
        )
        self.send_sms(transaction.user.phone_number,msg)







