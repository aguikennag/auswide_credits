from .models import NewsLaterSubscriber
from django import forms

class SubscribeForm(forms.ModelForm)  :
    
    class Meta() :
        model = NewsLaterSubscriber
        fields = '__all__'

    def clean_email(self)   :
        email = self.cleaned_data['email'] 
        if self.Meta.model.objects.filter(email = email).exists() :
            raise forms.ValidationError("You have already subscribed !")
        return email

class SendMailForm(forms.Form)  :
    receiver_name = forms.CharField(required = True,help_text="name of receiver") 
    subject = forms.CharField(required = True,help_text="topic of email") 
    receiver_email = forms.EmailField(required = True,help_text="email of receiver")     
    message = forms.CharField(required = True,widget=forms.Textarea)
   