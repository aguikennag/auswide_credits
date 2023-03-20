from django.urls import path,include
from .pages import Index,About,ModernBanking



urlpatterns = [
    path('',Index.as_view(),name = 'index'),
    path('about-us/',About.as_view(),name='about') ,
    path('careers/',About.as_view(),name='careers')  ,
    path('modern-banking/',ModernBanking.as_view(),name='modern-banking') ,
    
]