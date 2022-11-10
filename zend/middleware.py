from django.http import HttpResponse
from django.shortcuts import render


class AccountManagementMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # check if user is blocked
        restricted_paths = ['/accounts/']
        if request.user.is_authenticated:
            if request.user.is_blocked and any(request.path.startswith(base_path) for base_path in restricted_paths) :
                template_name = "custom-response.html"
                return render(request, template_name, locals())

        response = self.get_response(request)
        # Code to be executed for each request/response after
        # the view is called.

        return response
