from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from core.notification import Notification
from .forms import TransferForm, PinForm
from .models import Wallet, Transaction as transaction_model
from core.admin import AdminControls
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
import math
import time


class CompleteTransaction(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    this handles completeing ttransaction which were incomplete for one reason or the other
    using transaction id and making sure pin matches and user is owner of transaction"""
    feedback = {}
    transaction = None
    form_class = PinForm
    template_name = 'enter-pin.html'

    def get(self, request, *args, **kwargs):
        transact = None
        account = request.user.wallet
        form = self.form_class
        transact_id = kwargs['transact_id']
        try:
            transact = transaction_model.objects.get(
                transaction_id=transact_id)
            if transact.status == 'successful':
                return HttpResponse('This transaction has been processed completely')
            elif transact.status == 'processing':
                return HttpResponse('This transaction is already being processed,you will be notified when completed')

        except:
            return HttpResponse("Invalid request")
        if transact and not transact.transaction_type == "Internal Transfer":
            charge = settings.INTERNATIONAL_TRANSFER_CHARGE
            charge = (charge/100) * int(transact.amount)
            charge = round(charge, 2)
        else:
            charge = 0.00

        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        self.feedback = {}
        form = self.form_class(request.POST)
        if form.is_valid():
            # check pin match
            pin = form.cleaned_data['pin']
            if not pin == request.user.wallet.transaction_pin:
                self.feedback['error'] = "The Pin You entered is incorrect,please try again !"
                return JsonResponse(self.feedback)

            status = self.transaction.fulfill()
            msg = status.get("success") or msg.get("error")
            if msg:
                messages.success(request, msg)
            return JsonResponse(status)

        else:
            err = getattr(form, 'pin')
            self.feedback['error'] = err.errors

            return JsonResponse(self.feedback)

        return JsonResponse(self.feedback)

    def test_func(self):
        transact_id = self.kwargs['transact_id']
        try:
            transaction = transaction_model.objects.get(
                transaction_id=transact_id)
        except:
            return False
        # THE TRANSACTION OBJECT
        self.transaction = transaction
        return transaction.user == self.request.user


class Transfer(LoginRequiredMixin, View):

    template_name = 'transfer.html'
    form_class = TransferForm
    model2 = Wallet
    model = get_user_model

    def get(self, request, *args, **kwargs):

        account = request.user.wallet
        form = self.form_class
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        start = time.time()
        form = self.form_class(
            user=self.request.user,
            data=request.POST
        )
        if form.is_valid():
           
            error = None
            acc_num = form.cleaned_data.get('account_number')
            amount = form.cleaned_data.get('amount')
            transact_type = form.cleaned_data.get('transfer_type')
            # if internal
            receipient = None

            if transact_type == 'Internal Transfer':
                receipient = get_user_model().objects.get(account_number=acc_num)

            else:
                iban = form.cleaned_data.get('iban')
                bic = form.cleaned_data.get('bic')
                swift_number = form.cleaned_data.get('swift_number')
                # check if details is in our list,else give network error
                error = None

            acc_name, bank_name, country = None, None, None

            transact = transaction_model.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='debit',
                nature=form.cleaned_data['transfer_type'],
                description=form.cleaned_data['description'],
                charge=0.00,
                status="pending",
                status_message="Waiting for Transaction Pin Authorization",
                receiver=receipient,
                swift_number=form.cleaned_data.get('swift_number', None),
                iban=form.cleaned_data.get('iban', None),
                bic=form.cleaned_data.get('bic', None),
                account_number=acc_num,
                account_name=acc_name,
                country=country,
                bank_name=bank_name
            )

            return HttpResponseRedirect(reverse('complete-transaction', args=[transact.transaction_id]))

        else:
            return render(request, self.template_name, locals())
