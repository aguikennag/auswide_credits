from django.shortcuts import render
from django.views.generic import ListView, View, RedirectView, TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from .forms import ChangePinForm
from django.conf import settings
from django.contrib import messages


class Settings(LoginRequiredMixin, View):
    template_name = "settings.html"
    form_class = ChangePinForm

    def get(self, request, *args, **kwargs):
        ctx = {"change_pin_form": self.form_class}
        return render(request, self.template_name, ctx)


class ChangePin(LoginRequiredMixin, View):
    template_name = 'settings.html'
    form_class = ChangePinForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(user=request.user, data=request.POST)
        if form.is_valid():
            wallet = request.user.wallet
            wallet.transaction_pin = form.cleaned_data['new_pin']
            wallet.save()
            url = reverse('dashboard')
            messages.success(
                request,
                "You transaction pin was changed successfully"
            )
            return HttpResponseRedirect(url)
        
        else:
            return render(request, self.template_name, {"change_pin_form" : form})
