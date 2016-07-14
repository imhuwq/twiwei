from django.shortcuts import redirect

from functools import wraps


def login_required(func):
    from django.core.urlresolvers import reverse

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            return func(request, *args, **kwargs)
        return redirect(reverse('main:site_login'))

    return wrapper
