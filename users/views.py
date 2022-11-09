from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import PhoneNumberForm, EmailForm
from core.views import ValidationCode


class VerifyEmail(LoginRequiredMixin, View):
    template_name = 'email_verify.html'
    form_class = EmailForm

    def get(self, request, *args, **kwargs):

        form = self.form_class(initial={'email': request.user.email})
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST, user=request.user)
        if form.is_valid():
            # if email is edited
            new_email = form.cleaned_data['email']
            request.user.email = new_email
            request.user.email_verified = True
            request.user.save()

        else:
            return render(request, self.template_name, {'form': form})
        # success
        # send message
        msg = "Your email has been verified successfully,thanks for choosing us"
        if request.user.phone_number_verified:
            sms = Messages()
            sms.send_sms(request.user.phone_number, msg)

        if request.user.email_verified:
            mail = Email(send_type='support')
            mail.send_email([new_email], 'Email Verified successfully', msg)
        return render(request, "just_created.html", {})

    @staticmethod
    class SendCode(LoginRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            feedback = {}

            em = request.GET.get('email', None)
            if not em:
                feedback['error'] = "Email cannot be empty"
                return JsonResponse(feedback)
            ValidationCode.generate_code(
                request.user, email=em, send_type='email')
            feedback['success'] = 'Your verification code has been sent successfully,please check your email account'

            return JsonResponse(feedback)


class ValidatePhoneNumber(LoginRequiredMixin, View):
    template_name = 'phone_number_verify.html'
    form_class = PhoneNumberForm

    def get(self, request, *args, **kwargs):
        if request.user.phone_number_verified:
            return HttpResponse("Your phone number has already been verified")
        form = self.form_class(
            initial={'phone_number': request.user.phone_number})
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(data=request.POST, user=request.user)
        if form.is_valid():
            # if phone number is edited
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.phone_number_verified = True
            request.user.save()

        else:
            return render(request, self.template_name, {'form': form})
        # success
        msg = "Your phone number has been verified successfully,thanks for choosing us"
        if request.user.phone_number_verified:
            sms = Messages()
            sms.send_sms(request.user.phone_number, msg)

        if request.user.email_verified:
            mail = Email(send_type='support')
            mail.send_email([request.user.email], 'congrats', msg)

        return HttpResponseRedirect(reverse('validate-email'))

    @staticmethod
    class SendCode(LoginRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            feedback = {}
            try:
                pn = request.GET.get('phone_number', None)
                if not pn:
                    feedback['error'] = "phone number cannot be empty"
                ValidationCode.generate_code(request.user, phone_number=pn)
                feedback['success'] = 'Your verification code has been sent successfully'
            except:
                feedback['error'] = 'Oops!,an Error Occured please try again later !'

            return JsonResponse(feedback)
