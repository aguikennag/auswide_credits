from django.urls import reverse_lazy,reverse
from django.shortcuts import render
from django.views.generic import CreateView,View
from django.views.generic.base  import RedirectView
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate,login
from wallet.models import Wallet
from core.views import Email
from .models import  User,Dashboard
from .forms import UserCreateForm,PhoneNumberForm

class PasswordResetView() :
    template_name = 'password_reset_email.html'
    


class Register(CreateView) :
    template_name = 'register.html'
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('login')

    def auto_create_wallet(self,user,currency) :
        Wallet.objects.get_or_create(user = user,currency = currency)
        return

    def auto_create_dashboard(self,user)  :
        Dashboard.objects.get_or_create(user = user)
        return

    def post(self,request,*args,**kwargs) :
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid() :
            try : name = "{} {}".format(form.cleaned_data['first_name'],form.cleaned_data['last_name'])
            except : pass
            form.save(commit = False)
            form.instance.name = name
            user = form.save()
            
            #send thank you email 
            name = name or user.username
            
            self.auto_create_wallet(user,form.cleaned_data['currency'])
            self.auto_create_dashboard(user)
            
            
            mail = Email(send_type='support')
            
            ctx={'name' : name,'account_type' : user.account_type}
            mail.send_html_email([user.email],'Successful Signup','welcome-email.html',ctx=ctx)
            
            #authenticate and login user
            auth_user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'])
            if user is not None and user.is_active :
                login(request,auth_user)
            #redirect to validate email and phone number 
            return HttpResponseRedirect(reverse('validate-email'))
           
        else :
            return render(request,self.template_name,locals())    
      

    


class LoginRedirect(View)   :
    template_name = 'login_account_blocked.html'
    template_name2 = 'account_not_activated.html'
    
    def get(self,request,*args,**kwargs)  :
        #check if user is prevented from loggin in
        if request.user.is_activated : 
            return HttpResponseRedirect(reverse('dashboard'))
        else :
            return render(request,self.template_name2,locals())




    