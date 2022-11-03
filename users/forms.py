from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User
from wallet.models import Currency
from core.views import ValidationCode
from datetime import datetime


class UserCreateForm(UserCreationForm) :
    currency =  forms.ModelChoiceField(queryset=Currency.objects.all(),required=True)
  
    class Meta(UserCreationForm.Meta) :
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name','last_name','username','email','account_type','country','address','phone_number','occupation','passport','date_of_birth')
        
        widgets = {
            'date_of_birth' : forms.TextInput(attrs={'type': 'date'})
        }
        

class ProfileUpdateForm(ModelForm) :
    class Meta() :
        model  = User
        fields = ['first_name','last_name','email','phone_number','country','occupation']
        widgets = {
            
            'first_name' : forms.TextInput(attrs={'readonly':False}),
            'last_name' : forms.TextInput(attrs={'readonly':False}),
            'phone_number' : forms.TextInput(attrs={'readonly':False}),
            'country' : forms.TextInput(attrs={'readonly':False}),
            'occupation' : forms.TextInput(attrs={'readonly':False}),
            'email' : forms.TextInput(attrs={'readonly':False}),
        }

  
class PhoneNumberForm(ModelForm) :
    code = forms.CharField(required=True,help_text="Enter the code sent to you,click resend if you dint get any after some time")
    
    def __init__(self,user=None,*args,**kwargs) :
        self.user = user
        super(PhoneNumberForm,self).__init__(*args,**kwargs)
    
    class Meta() :
        model = User
        fields  = ['phone_number'] 

        widgets = {
            'phone_number' : forms.TextInput(attrs={'id' : "phone_number"}),
        }  

        help_texts = {
            'phone_number' : "We are sending a verification code to this phone number,you can edit it before hitting the send button"
        } 

    def clean_code(self) :
        code = self.cleaned_data['code']  
        validated,error = ValidationCode.validate_otc(self.user,code)
        if not validated :
            raise forms.ValidationError(error)
        return code



class EmailForm(ModelForm) :
    code = forms.CharField(required=True,help_text="Enter the code sent to your email,click resend if you dint get any after some time")
    
    def __init__(self,user=None,*args,**kwargs) :
        self.user = user
        super(EmailForm,self).__init__(*args,**kwargs)
    
    class Meta() :
        model = User
        fields  = ['email'] 

        widgets = {
            'email' : forms.TextInput(attrs={'id' : "email"}),
        }  

        help_texts = {
            'email' : "We are sending a verification code to this email address,you can edit it before hitting the send button"
        } 

    def clean_code(self) :
        code = self.cleaned_data['code']  
        validated,error = ValidationCode.validate_otc(self.user,code)
        if not validated :
            raise forms.ValidationError(error)
        return code        


class CreditCardForm(forms.Form)  :
    type_choice = (('Debit Card','Debit Card'),('Credit Card','Credit Card'))
    model_choice = (('Mastercard','Mastercard'),('Visacard','Visacard'))
    card_type = forms.ChoiceField(choices = type_choice)
    card_model = forms.ChoiceField(choices = model_choice)
    name_on_card = forms.CharField(help_text = "Exactly as you want on card")
    address = forms.CharField(required = False,help_text="This is the location where your card will be delivered,leave blank to use your registered address")


class AccountStatementForm(forms.Form)  :
    start = forms.DateField(widget=forms.SelectDateWidget())
    end = forms.DateField(widget=forms.SelectDateWidget())

    

class LoanForm(forms.Form) :
    type_choices = (
    ('Business Term Loan','Business Term Loan'),
    ('Business Equity Installment Loan','Business Equity Installment loan'),
    ('Investment real Estate Term Loan','Investment real Estate Term Loan'),
    ('Auto loan','Auto Loan'),
    ('Student loan','Student loan'),
    ('Personal Loan','Personal Loan'),
    ('Others(tell us about it in your description)','Others'),
    )
    loan_type = forms.ChoiceField(choices = type_choices,initial="Select Loan Type")
    amount = forms.FloatField(help_text='USD')
    loan_duration = forms.IntegerField(help_text = "in months")
    description = forms.CharField(widget = forms.Textarea)




