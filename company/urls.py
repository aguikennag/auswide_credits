from django.urls import path,include
from . import pages,services



urlpatterns = [

    path('',pages.Index.as_view(),name = 'index'),
    path('about-us/',pages.About.as_view(),name='about') ,
    path('contact-us/',pages.Contact.as_view(),name='contact') ,
    path('faq/',pages.FAQ.as_view(),name='faq') ,
    path('careers/',pages.Careers.as_view(),name='career') ,


    #SERVICES 
    path('services/accounts/',services.Accounts.as_view(),name='services-accounts') ,
    path('services/cards/',services.Cards.as_view(),name='services-cards') ,
    path('services/loans/',services.Loans.as_view(),name='services-loan') ,


]