from .models import NewsLaterSubscriber,Notification as Notification_model
from .forms import SubscribeForm
from django.http import JsonResponse
from django.views.generic import View


class Notification() :
    @staticmethod
    def notify(user,message) :
        Notification_model.objects.create(user = user,message = message)

    

class Subscribe(View) :
    form_class = SubscribeForm
    model = NewsLaterSubscriber
    def post(self,request,*args,**kwargs) :
        feedback = {}
        form = self.form_class(request.POST)
        if form.is_valid() :
            form.save()
            feedback['success'] = 'subscribed'
        else : feedback['error'] = form.errors['email']    
        return JsonResponse(feedback)