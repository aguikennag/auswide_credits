from django import forms
from .models import Wallet,Currency
from django.contrib.auth import get_user_model
from django.conf import settings


class TransferForm(forms.Form) :


    TypeChoices = (('Internal Transfer','Internal Transfer'),('International Transfer','International Transfer'))
    transfer_type  = forms.ChoiceField(choices= TypeChoices)
    account_number = forms.CharField(required= False,help_text="receipient account number")
    iban = forms.CharField(required = False,label = 'IBAN',help_text="international bank identification number")
    swift_number = forms.CharField(required = False,label="Swift/ABA Routing Number",help_text="")
    bic =  forms.CharField(required = False,label="BIC",help_text="Bank identification code")
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
                raise forms.ValidationError("""The entered account number does not belong to any {} account,
                you are getting this error because you selected an internal transfer""".format(
                    settings.SITE_NAME
                ))
            if self.user.account_number == acc_num :
                raise forms.ValidationError("the entered account number matches your account, this is not allowed")
        
        return acc_num


    def clean_ibxan(self) :
        iban = self.cleaned_data.get('iban')
        if self.cleaned_data['transfer_type']  == "International Transfer"  and  len(iban) < 1 :
            raise forms.ValidationError("Iban number cannot be empty for {} ".format(self.cleaned_data['transfer_type']))
        return iban  
         

    def clean_swift_number(self) :
        swift_number = self.cleaned_data.get('swift_number')
        if  len(swift_number) < 1 :
            return swift_number
        return swift_number 

    """def clean_bic(self) :
        bic = self.cleaned_data['bic']
        if self.cleaned_data['transfer_type']  != "Internal Transfer"  and  len(bic) < 1 :
            raise forms.ValidationError("BIC cannot be empty for {} ".format(self.cleaned_data['transfer_type']))
        return bic"""  

    def get_transfer_charge(self) :
        """charge_due_amount = 0.08 * amount 
        charge = max_charge if max_charge < charge_due_amount else charge_due_amount"""        

    def clean_amount(self) :
        amt = self.cleaned_data['amount']   
        amt = int(amt)
        if amt < 1 :
            raise forms.ValidationError("Amount is not valid, please enter a valid amount")
        
        if amt > self.user.wallet.available_balance :
            raise forms.ValidationError("Your available balance is insufficient to make this transaction, Enter a lower amount")
        return amt   


        
class PinForm(forms.Form) :
    pin = forms.CharField(
        required = True,
        widget=forms.TextInput(attrs={'type': 'password'}),
        help_text="Enter your transaction pin to complete your transaction"
        )

    def clean_pin(self) :
        pin = self.cleaned_data['pin']
        #check if its valid
        return pin


