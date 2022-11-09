from django.urls import reverse_lazy,reverse
from django.shortcuts import render
from django.views.generic import CreateView,View
from django.views.generic.base  import RedirectView
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate,login
from wallet.models import Wallet

from .models import  User,Dashboard
from .forms import UserCreateForm,PhoneNumberForm

class PasswordResetView() :
    template_name = 'password_reset_email.html'
    


class Register(CreateView) :
    template_name = 'register.html'
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('login')

 

    def post(self,request,*args,**kwargs) :
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid() :
            user = form.save()
            Wallet.objects.get_or_create(user = user,currency = form.cleaned_data.get("currency"))
    
            #authenticate and login user
            auth_user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            if user is not None and user.is_active :
                login(request,auth_user)

            #redirect to validate email and phone number 
            return HttpResponseRedirect(reverse('dashboard'))
           
        else :
            return render(request,self.template_name,locals())    
      

    


class LoginRedirect(View)   :
    
    def get(self,request,*args,**kwargs)  :
        return HttpResponseRedirect(reverse('dashboard'))




    