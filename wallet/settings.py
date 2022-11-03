from django.shortcuts import render
from django.views.generic import View,FormView
from django.contrib.auth import get_user_model
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from core.notification import Notification
from urllib.parse import urlparse,urlunparse,urljoin 
from .forms import TransferForm,PinForm,ChangePinForm
from .models import Wallet,Transaction as transaction_model
from .helpers import Transaction


class ChangePin(LoginRequiredMixin,View) :
    template_name = 'form.html'
    form_class = ChangePinForm

    def get(self,request,*args,**kwargs) :
        form = self.form_class
        return render(request,self.template_name,locals())

    def post(self,request,*args,**kwargs) :
        form = self.form_class(user=request.user,data=request.POST) 
        if form.is_valid() :
            wallet = request.user.wallet
            wallet.transaction_pin = form.cleaned_data['new_pin']
            wallet.save()
            url = urljoin(reverse('dashboard'),"?chgp=dlkp")
            return HttpResponseRedirect(url)
        else :
            return render(request,self.template_name,locals())   


