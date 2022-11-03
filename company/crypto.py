from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

class CryptoConverter(View) :
    def access_api() :
        pass
    
    def get(self,request,*args,**kwargs) :
        feedback =  {}
        crypto_base = request.GET.get('crypto','BTC')
        crypto_amount = request.GET.get('cryto_amount',1)
        to_curr = request.GET.get('to_curr',"USD")

        return JsonResponse(feedback)
