
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
        if not account.allowed_to_transact:
            response = request.user.wallet.disallow_reason or ""
            return HttpResponse(response)
        form = self.form_class
        transact_id = kwargs['transact_id']
        try:
            transact = transaction_model.objects.get(
                transaction_id=transact_id)
            if transact.status == 'Successful':
                return HttpResponse('This transaction has been processed completely')
            elif transact.status == 'Processing':
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
            
            if not request.user.wallet.allowed_to_transact:
                self.feedback['error'] = request.user.wallet.disallow_reason or ""
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

    # for swift_number,first 4 is for bank code,next 2 is country,next two is state/city code,
    # optional 3 for branch
    allowable_transaction = [
        {
            'account_name': 'Ruriya Karat',
            'account_number': '7421681361',
            'swift_number': 'UOVBTHBK',
            'bank_name': '  United Overseas Bank',
            'country': 'Thailand',

        },

        {
            'account_name': 'Jerry. I. Ezisi',
            'account_number': '94275900101',
            'iban': 'TR530020500009427590000101',
            'swift_number': 'KTEFTRISXXX',
            'bank_name': 'KuveytTurk bank',
            'country': 'Turkey',

        },
        {
            'account_name': 'Stefanie beyfuss',
            'iban': 'DE38793400540230463200',
            'swift_number': 'COBADEFFXXX',
            'bank_name': 'Commerzbank',
            'country': 'Germany',
        },
        {
            'account_name': 'Jerry. I. Ezisi',
            'iban': 'TR960020500009427590000103',
            'swift_number': 'KTEFTRISXXX',
            'account_number': '94275900103',
            'bank_name': 'uveyt Türk bank',
            'country': 'Turkey',
        },
        {
            'account_name': 'Kerstin Baldeau',
            'iban': 'DE46265659281005930000',
            'bic': 'GENODEF1HGM',
            'bank_name': 'Volksbank (GHB)',
            'country': 'Germany',
        },
        {
            'account_name': 'MarieAnn Sablan Sapien',
            'account_number': '885083555',
            'swift_number': '325070760',
            'bank_name': 'Chase Bank',
            'country': 'United States of America',
        },
        {
            'account_name': 'John Kuregian',
            'account_number': '6030827205',
            'swift_number': '121000248',
            'bank_name': 'Wells Fargo bank',
            'country': 'United States of America',
        },
        {
            'account_name': 'SIXTUS CHIGAEMEZU ISHIA',
            'account_number': '10363287050',
            'iban': 'TR470006400000210363287050',
            'swift_number': 'ISBKTRISXXX',
            'bank_name': 'TURKIYE BANKASI',
            'country': 'Turkey',

        },

        {
            'account_name': 'Birgit Hengelage',
            'iban': 'DE36100110012621610891',
            'bic': 'NTSBDEB1XXX',
            'bank_name': 'N26',
            'country': 'Germany',
        },

        {
            'account_name': 'Fischer Albert',
            'iban': 'DE79100110012629910310',
            'bic': 'NTSBDEB1XXX',
            'bank_name': 'N26',
            'country': 'Germany',
        },

        {
            'account_name': 'Moura Construction LTD.',
            'account_number': '72612522',
            'iban': 'GB08SRLG60837172612522',
            'swift_number': 'SRLGGB2L',
            'bank_name': 'Starling Bank',
            'country': 'United Kingdom'
        },


        {
            'account_name': 'Ingrida Glodaite',
            'iban': 'DE12280501000001794239',
            'bic':  'SLZODE22',
            'bank_name': 'Landessparkasse zu Oldenburg',
            'country': 'Germany'
        },


        {
            'account_name': 'Endang Suliwidiarti',
            'account_number': '2670438751',
            'swift_number': 'CENAIDJA',
            'bank_name': 'Bank Central Asia',
            'country': 'Indonesia'
        },
    ]

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

    
    """def post(self, request, *args, **kwargs):
        start = time.time()
        form = self.form_class(user=self.request.user, data=request.POST)
        if form.is_valid():
            details, error = None, None
            acc_num = form.cleaned_data['account_number']
            amount = form.cleaned_data['amount']
            transact_type = form.cleaned_data['transfer_type']
            # if internal
            receipient = None
            if transact_type == 'Internal Transfer':
                charge = 0.00
                receipient = get_user_model().objects.get(account_number=acc_num)

            else:

                # check if details match for international transfer 
                if transact_type != "Internal Transfer":
                    delay_time = 4
                    charge = settings.INTERNATIONAL_TRANSFER_CHARGE or 2
                    charge = (charge/100) * int(amount)
                    iban = form.cleaned_data['iban']
                    bic = form.cleaned_data['bic']
                    swift_number = form.cleaned_data['swift_number']
                    # check if details is in our list,else give network error
                    details, error = None, None
                    for info in self.allowable_transaction:

                        if info.get('account_number', '$#^') == acc_num or info.get('iban', '.!#') == iban:
                            # checking if other details match
                            # info.get('iban','') == iban or info.get('bic','') == bic
                            if 1:
                                if info.get('swift_number', None):

                                    # swift can be empty
                                    if info.get('swift_number', '~!@!') == swift_number:
                                        details = info

                                    else:
                                        delayed = time.time() - start
                                        if delayed < delay_time:
                                            time.sleep(delay_time-delayed)
                                            error = "Data Mismatch ! Entered data does not match with info associated with the account number/IBAN, please crosscheck !"

                                else:
                                    if swift_number:
                                        error = "The account matching  the entered iban is not associated with a swift number(this is not a united states account), please crosscheck!"
                                        delayed = start - time.time()
                                        if delayed < delay_time:
                                            time.sleep(delay_time-delayed)

                                    else:
                                        details = info
                                        delayed = start - time.time()
                                        if delayed < delay_time:
                                            time.sleep(delay_time-delayed)

                            else:
                                delayed = time.time() - start

                                if delayed < delay_time:
                                    time.sleep(delay_time-delayed)
                                error = "Data Mismatch !,Entered data does not match iban info, please crosscheck !"

                    # assuming no match
                    if not details:
                        delayed = time.time() - start

                        if delayed < delay_time:
                            time.sleep(delay_time-delayed)
                        error = error or "Request Time Out, please Try again later. if situation persists, please contact customer care"
                        return render(request, self.template_name, locals())

            # check if user has the amount
            if request.user.wallet.available_balance < float(amount + charge):
                error = "Insufficient Funds,Enter a lower amount"
                return render(request, self.template_name, locals())
            else:

                # create transaction,but its still pending because of pin issues
                if details:
                    acc_name = details.get('account_name')
                    bank_name = details.get('bank_name')
                    country = details.get('country')
                else:
                    acc_name, bank_name, country = None, None, None

                transact = transaction_model.objects.create(
                    user=request.user,
                    amount=amount,
                    transaction_type='Debit',
                    nature=form.cleaned_data['transfer_type'],
                    description=form.cleaned_data['description'],
                    charge=charge,
                    status="Pending",
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

                time.sleep(delay_time)
                return HttpResponseRedirect(reverse('complete-transaction', args=[transact.transaction_id]))
        else:
            return render(request, self.template_name, locals())
    """