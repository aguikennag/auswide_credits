from django import forms
from .models import Wallet,Currency
from django.contrib.auth import get_user_model


class TransferForm(forms.Form) :


    TypeChoices = (('Internal Transfer','Internal Transfer'),('International Transfer','International Transfer'))
    transfer_type  = forms.ChoiceField(choices= TypeChoices)
    account_number = forms.CharField(required= False)
    iban = forms.CharField(required = False,label = 'IBAN',help_text="leave blank only for internal transfers")
    swift_number = forms.CharField(required = False,label="Swift/ABA Routing Number",help_text="")
    bic =  forms.CharField(required = False,label="BIC",help_text="leave blank only for internal transfers,and transfers to canada and american accounts ")
    #currency = forms.ModelChoiceField(queryset=Currency.objects.all())
    amount = forms.FloatField()
    description = forms.CharField()

    def __init__(self,user  = None,*args,**kwargs) :
        super(TransferForm,self).__init__(*args,**kwargs)
        self.user = user 
    


    def clean_account_number(self) :

        acc_num = self.cleaned_data['account_number']
        if self.cleaned_data['transfer_type']  == "Internal Transfer" :
            if not get_user_model().objects.filter(account_number = acc_num).exists() :
                raise forms.ValidationError("The entered account number does not belong to any credo finance bank valid account,you are getting this error because you selected an internal transfer")
            if self.user.account_number == acc_num :
                raise forms.ValidationError("the entered account number matches yours,this is not allowed")
        return acc_num


    def clean_ibxan(self) :
        iban = self.cleaned_data['iban']
        if self.cleaned_data['transfer_type']  != "Internal Transfer"  and  len(iban) < 1 :
            raise forms.ValidationError("Iban number cannot be empty for {} ".format(self.cleaned_data['transfer_type']))
        return iban  
         

    def clean_swift_number(self) :
        swift_number = self.cleaned_data['swift_number']
        if  len(swift_number) < 1 :
            return None
        return swift_number 

    """def clean_bic(self) :
        bic = self.cleaned_data['bic']
        if self.cleaned_data['transfer_type']  != "Internal Transfer"  and  len(bic) < 1 :
            raise forms.ValidationError("BIC cannot be empty for {} ".format(self.cleaned_data['transfer_type']))
        return bic"""      

    def clean_amount(self) :
        amt = self.cleaned_data['amount']   
        if int(amt) < 1 :
            raise forms.ValidationError("Amount cannot be less than 1,please enter a valid amount")
        return amt   

        
class PinForm(forms.Form) :
    pin = forms.CharField(required = True,widget=forms.TextInput(attrs={'type': 'password'}))

    def clean_pin(self) :
        pin = self.cleaned_data['pin']
        #check if its valid
        return pin



class ChangePinForm(forms.Form) :
    old_pin = forms.CharField(required = True,help_text="Enter Your Old Pin")
    new_pin = forms.CharField(required = True,help_text="Enter Your New Pin(4 digits)")

    def __init__(self,user  = None,*args,**kwargs) :
        super(ChangePinForm,self).__init__(*args,**kwargs)
        self.user = user 


    def clean_old_pin(self) :
        o_pin = self.cleaned_data['old_pin']
        if o_pin !=  self.user.wallet.transaction_pin :
            self.o_pin = o_pin
            raise forms.ValidationError("Pin Mismatch !,Your old pin  does not match please contact support")

        return  o_pin 

    def clean_new_pin(self) :
        new_pin = self.cleaned_data['new_pin']
       
        if len(new_pin) != 4 :
            raise forms.ValidationError("Pin Must be exactly 4 digits")
        #if self.o_pin == new_pin :
            #raise forms.ValidationError("Sorry !,your old pin corresponds to your new pin") 
        return  new_pin     


