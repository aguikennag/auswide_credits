from django.urls import path,include
from .pages import Index,Services,TOS,About,Contact,Faq,LoanView
from .services import Services


urlpatterns = [
    path('',Index.as_view(),name = 'index'),
    path('help-center/',Faq.as_view(),name='faq'),
    path('about-us/',About.as_view(),name='about') ,
    path('careers/',About.as_view(),name='careers')  ,
    path('modern-banking/',About.as_view(),name='modern-banking') ,
    
]