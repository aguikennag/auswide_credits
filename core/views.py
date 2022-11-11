from pipes import Template
from re import template
from django.shortcuts import render
from django.views.generic import RedirectView,View,TemplateView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string,get_template
from django.conf import settings
from django.utils import timezone
from core.helpers import currency_convert
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



class TestTemplate(TemplateView) :
    template_name = "403.html"

    def get_context_data(self, **kwargs)  :
        from wallet.models import Transaction
        ctx = super(TestTemplate,self).get_context_data(**kwargs)
        ctx['transaction'] = Transaction.objects.all()[0]
        return ctx



def error_404_handler(request,exception) :
    template_name = "404.html"
    return render(request,template_name,locals())


def error_500_handler(request) :
    template_name = "500.html"
    return render(request,template_name,locals())

def error_403_handler(request,exception) :
    template_name = "403.html"
    return render(request,template_name,locals())


