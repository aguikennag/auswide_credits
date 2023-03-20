
from django.shortcuts import render
from django.views.generic import RedirectView,View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string,get_template
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
#import imgkit
from io import BytesIO
#from  xhtml2pdf import pisa
import random
#from twilio.rest import Client
from django.core.mail import EmailMultiAlternatives, SafeMIMEMultipart
from email.mime.image import MIMEImage

from core.templatetags.vocabulary import capitalize
from .helpers import currency_convert
import os



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






class TransactionMail() :

    def __init__(self,transaction) :
        self.transaction = transaction
        self.mail = Email("transaction")

    def send_transaction_mail(self) :
        template_name = "transaction/transaction-mail.html"
        self.mail.send_html_email(
            [self.transaction.user.email],
            template_name,
            subject= "{} transaction occured on your account".format(capitalize(self.transaction.transaction_type)),
            ctx = {"transaction" : self.transaction }
        )
       

  
  

class AccountMail() :
    def __init__(self,user) :
        self.user = user
      
    def send_registration_email(self) :
        mail = Email("support")
        welcome_text = """
            we are happy to have you onboard of a new era banking and finance management, we the team
            at <b>{}</b> take the safety of your finance very seriously, we are happy to usher you into a new world of an enhanced 
            baking experience.
            """.format(settings.SITE_NAME)

        mail.send_html_email(
            [self.user.email],
            template="email/registration/registration-mail.html",
            subject = "Welcome to {}".format(settings.SITE_NAME),
            ctx = {"text" : welcome_text,"name" : self.user.name}
            )   


    def send_verification_code(self,email,code)   :
        mail = Email("security")
        mail.send_html_email(
            [email],
            template="verification-code-mail.html",
            subject = "{} Verification Code".format(settings.SITE_NAME),
            ctx = {"code" : code,"verification_code_validity" : 5 }
            )      





class Email() :
    def __init__(self,send_type = "support") :

        from django.core.mail import get_connection

        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT
        password = settings.EMAIL_HOST_PASSWORD

        senders = {
            'support' : settings.EMAIL_HOST_USER_SUPPORT,
            "security" : settings.EMAIL_HOST_USER_SUPPORT,
            "transaction" : settings.EMAIL_HOST_USER_TRANSACTION,
        }

        if not send_type :
           self.send_from = senders['support']

        else :
            self.send_from = senders.get(send_type,senders['support'])
        
        self.auth_connecion = get_connection(
            host = host,
            port = port,
            username = self.send_from,
            password = password,
            use_tls = settings.EMAIL_USE_TLS
        ) 


    
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


    def send_html_email(self,receive_email_list,template = None,subject =None,files_path_list=None,ctx=None) :
        error = None #for error control
        subject = subject or self.default_subject
        template = template or self.default_template
        ctx = ctx
        ctx['site_name'] = settings.SITE_NAME
        msg = render_to_string(template,ctx)
        
        email = EmailMultiAlternatives(
            subject,
            msg,
            self.send_from,
            receive_email_list,
            connection=self.auth_connecion
            )
        email.content_subtype = "html"
        email.mixed_subtype = "related"
 
        BASE_DIR = settings.STATIC_URL
        logo_path = os.path.join(settings.BASE_DIR,"static/img/logo.png")
        with open(logo_path,'rb') as f :
            logo = MIMEImage(f.read())
            logo.add_header("Content-ID","<logo.png>")
            email.attach(logo)
            
        """if isinstance(files_path_list,list) :
            for file in files_path_list :
                "fetch image"
                with open(file,"rb") as f :
                    image = MIMEImage(f.read())"""
        """with open(logo_path, mode='rb') as f :
            image = MIMEImage(f.read())
            email.attach(image)
            image.add_header('Content-ID',"<logo>") """   
    
        #if settings.DEBUG : print(msg)  
        try :
            email.send()
        except : 
            error = "mail was not sent successfully"
            print(error)
        self.auth_connecion.close()
        
        return error
        
        


    def send_file_email(self,file_name,_file,receive_email_list,subject,message) :
        email = EmailMessage(subject,message,self.send_from,receive_email_list,connection=self.auth_connecion)
        email.attach(file_name,_file)
        try : 
            email.send()
            self.auth_connecion.close()
        except : pass


 

    
   
 
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
                    






