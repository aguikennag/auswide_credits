from django.shortcuts import render
from django.views.generic import TemplateView,View
from django.http import JsonResponse
from django.core.mail import send_mail




class Accounts(TemplateView) :
    template_name = 'services-accounts.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(Accounts,self).get_context_data(*args,**kwargs) 
       
        return context
    


class Loans(TemplateView) :
    template_name = 'services-loans.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(Loans,self).get_context_data(*args,**kwargs) 
        return context



class Cards(TemplateView) :
    template_name = 'services-cards.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(Cards,self).get_context_data(*args,**kwargs) 
        return context        