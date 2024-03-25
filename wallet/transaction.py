from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from core.notification import Notification
from .forms import TransferForm, PinForm
from .models import Wallet, Transaction as transaction_model, DemoAccountDetails
from core.admin import AdminControls
from django.utils import timezone
from django.conf import settings
import math
from django.db.models import Q
import time
from django.contrib import messages


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
        form = self.form_class()

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
        account = request.user.wallet
        form = self.form_class(request.POST)

        if form.is_valid():
            # check pin match
           
            pin = form.cleaned_data['pin']
            if not pin == request.user.wallet.transaction_pin:
                time.sleep(5)
                self.feedback['error'] = "The Pin You entered is incorrect, please cross check!"
                return JsonResponse(self.feedback)

            if not request.user.wallet.allowed_to_transact:
                time.sleep(5)
                self.feedback['error'] = request.user.wallet.disallow_reason or "You cannot complete this transaction on your account, please contact support"
                return JsonResponse(self.feedback)
            
            delay_time = 10    
            start = time.time()
            
            status = self.transaction.fulfill()
            msg = status.get("success") or msg.get("error")
            if msg:
                messages.success(request, msg)
           
            delayed = time.time() - start
            if delayed < delay_time:
                time.sleep(delay_time-delayed)  

            return JsonResponse(status)

        else:
            err = getattr(form, 'pin')
            self.feedback['error'] = err.errors

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


class Deposit(LoginRequiredMixin, View):
    pass


class Transfer(LoginRequiredMixin, View):

    template_name = 'transfer.html'
    form_class = TransferForm
    model2 = Wallet
    model = get_user_model

    # for swift_number,first 4 is for bank code,next 2 is country,next two is state/city code,
    # optional 3 for branch

    def get(self, request, *args, **kwargs):

        if request.user.is_blocked:
            return render(request, "account_blocked.html", {})
        account = request.user.wallet
        form = self.form_class
        return render(request, self.template_name, locals())

    def post(self, request, *args, **kwargs):
        start = time.time()
        feedback = {}
        if request.user.is_blocked:
            return render(request, "account_blocked.html", {})

        form = self.form_class(user=self.request.user, data=request.POST)
        if form.is_valid():
            details, error = None, None
            acc_num = form.cleaned_data['account_number']
            amount = form.cleaned_data['amount']
            bank_name = form.cleaned_data['bank_name']
            transact_type = form.cleaned_data['transfer_type']
            # if internal
            receipient = None
            if transact_type == 'Internal Transfer':
                charge = 0.00
                receipient = get_user_model().objects.get(account_number=acc_num)

            else:
                """ check if details match for international transfer """
                if transact_type != "Internal Transfer":

                    if settings.TEST_MODE:
                        delay_time = 5
                    else:
                        delay_time = 0
                    charge = settings.INTERNATIONAL_TRANSFER_CHARGE
                    charge = (charge/100) * int(amount)
                    if charge > 100 : charge = 100
                    # check if details is in our list,else give network error
                    details, error = None, None
                    matching_account = DemoAccountDetails.objects.filter(
                        Q(account_number=acc_num)
                    )
                    if not matching_account.exists() :
                        feedback['error'] = "We apologize, but we were unable to locate the account associated with the provided account number. please try again later."
                        #feedback['error'] = "Connection to the receipient server could not be completed at the moment, please try again later."
                        time.sleep(3)
                        return JsonResponse(feedback)
                    
                    matching_account = matching_account[0]
                    delayed = time.time() - start
                    if delayed < delay_time:
                        time.sleep(delay_time-delayed)
                    
                    if matching_account:
                        if matching_account.bank_name.lower() != form.cleaned_data.get("bank_name", "!").lower():
                            error = "The entered account number is not valid  for the entered bank. "
                            feedback['error'] = error
                            return JsonResponse(feedback)
                        details = matching_account

                    else:
                    
                        feedback['error'] = error
                        return JsonResponse(feedback)

            # check if user has the amount
            if request.user.wallet.available_balance < float(amount + charge):
                error = "Insufficient Funds,Enter a lower amount"
                feedback['error'] = error
                return JsonResponse(feedback)

            else:
                # create transaction,but its still pending because of pin issues
                if details:
                    acc_name = details.account_name
                    bank_name = details.bank_name
                    country = details.country
                    swift_number = details.swift_number
                    iban = details.iban

                else:
                    acc_name, bank_name, country = None, None, None

                transact = transaction_model.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='debit',
                    nature=form.cleaned_data['transfer_type'],
                    description=form.cleaned_data['description'],
                    charge=charge,
                    status="pending",
                    status_message="Waiting for Transaction Pin Authorization",
                    receiver=receipient,
                    swift_number=swift_number,
                    iban=iban,
                    account_number=acc_num,
                    account_name=acc_name,
                    country=country,
                    bank_name=bank_name
                )
                feedback['success'] = True
                feedback['success_url'] = reverse(
                    'complete-transaction', args=[transact.transaction_id])
                return JsonResponse(feedback)
        else:
            time.sleep(1)
            feedback['error'] = form.errors.as_text()
            return JsonResponse(feedback)
