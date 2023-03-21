from django.shortcuts import render
from django.views.generic import TemplateView,View
from django.http import JsonResponse
from django.template.loader import render_to_string
from .forms import ContactForm
from django.core.mail import EmailMessage,send_mail


class Index(TemplateView) :
    template_name = 'index.html'

    def get(self,request,*args,**kwargs) :
        
        return render(request,self.template_name,locals())

    def get_context_data(self,*args,**kwargs) : 
        context = super(Index,self).get_context_data(*args,**kwargs) 
        return context
        

class About(TemplateView) :
    template_name = 'home.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(About,self).get_context_data(*args,**kwargs) 
       
        return context



class Contact(TemplateView) :
    template_name = 'contact.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(Contact,self).get_context_data(*args,**kwargs) 
       
        return context




class ModernBanking(TemplateView) :
    template_name = "modern-banking.html"