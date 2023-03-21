from django.urls import path,include
from .pages import Index,About,ModernBanking,Contact



urlpatterns = [
    path('',Index.as_view(),name = 'index'),
    path('about-us/',About.as_view(),name='about') ,
    path('contact-us/',Contact.as_view(),name='contact') ,
    path('careers/',About.as_view(),name='careers')  ,
    path('modern-banking/',ModernBanking.as_view(),name='modern-banking') ,
    
]