from django.shortcuts import render
from django.views.generic import TemplateView,View
from django.http import JsonResponse
from django.core.mail import send_mail



class Services(TemplateView) :
    template_name = 'services.html'

    def get_context_data(self,*args,**kwargs) : 
        context = super(Services,self).get_context_data(*args,**kwargs) 
       
        return context