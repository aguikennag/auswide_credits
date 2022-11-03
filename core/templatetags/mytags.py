from django import template
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.helpers import Helper

register = template.Library()

@register.filter
def currency_convert(amt,currencies) :
    try: 
        _from,_to = tuple(currencies.split('_'))
        _from,_to = str(_from),str(_to)
        result  = Helper.currency_convert(amt,_from,_to)
        return str(result)
    except : return None    
   

@register.filter(name = 'intdivide')
def  intdivide(value,div) :
    try :
        return int(value)//int(div)
    except (ValueError,ZeroDivisionError) : 
        return None



                    


            
        






