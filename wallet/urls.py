from django.urls import path,include
from .transaction import Transfer,CompleteTransaction



urlpatterns = [
    #TRANSACTION
    path('send-money/',Transfer.as_view(),name='transfer'),
    path('<str:transact_id>/complete-transacton/',CompleteTransaction.as_view(),name='complete-transaction'),





]