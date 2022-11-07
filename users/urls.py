from django.urls import path, include
from .accounts import Register, LoginRedirect
from .dashboard import (
    Dashboard,
    Profile,
    TransactionHistory,
    AccountStatement
)
from .settings import Settings, ChangePin
from .views import ValidatePhoneNumber, VerifyEmail

urlpatterns = [
    path('account/', Dashboard.as_view(), name='dashboard'),
    path('account/create/', Register.as_view(), name='register'),
    path('account/info/', Profile.as_view(), name='profile'),
    path('account/settings/', Settings.as_view(), name="settings"),

    # transaction
    path('transactions/history/', TransactionHistory.as_view(),
         name='transaction-history'),
    path('statement/', AccountStatement.as_view(), name='account-statement'),

    path('login/', LoginRedirect.as_view(), name="login-redirect"),

    # SETTINGS
    path("account/update-transaction-pin/",
         ChangePin.as_view(), name="change-transaction-pin"),

    # account
    # path('verify-phone-number/',ValidatePhoneNumber.as_view(),name='validate-phone-number'),
    #path('verify-phone-number/send-code/',ValidatePhoneNumber.SendCode.as_view(),name= 'validate-phone-number-send-code'),

    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('verify-email/send-code', VerifyEmail.SendCode.as_view(),
         name='validate-email-send-code')

]
