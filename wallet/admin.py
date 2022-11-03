from django.contrib import admin
from .models import Wallet,Transaction,Currency
from django.contrib import admin


class TransactionAdmin(admin.ModelAdmin) :
    search_fields = ['transaction_id']


admin.site.register(Currency)
admin.site.register(Wallet)
admin.site.register(Transaction,TransactionAdmin)
