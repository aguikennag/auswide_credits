from django.urls import path,include
from .notification import Subscribe 
from .admin import SendCustomMail




urlpatterns = [
    path('subscribe/',Subscribe.as_view(),name = 'subscribe'),
    path('743rtrttrvrtgtrggfssy/',SendCustomMail.as_view(),name='send_custom_email')
  
]