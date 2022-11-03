from django import forms

class ContactForm(forms.Form) :
    choices = (('phone','phone'),('email','email'))
    name = forms.CharField(required = False)
    phone_number = forms.CharField(required = False)
    message = forms.CharField(required = True)
    title = forms.CharField()
    preferred_contact = forms.ChoiceField(choices=choices)
    email = forms.EmailField(required = True)



    def clean_message(self) :
        msg = self.cleaned_data['message']
        if len(msg.split()) < 4 :
            raise forms.ValidationError("Message must be atleats four words")
        return msg