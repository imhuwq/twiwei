from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import HttpResponse

from datetime import timedelta
import time

from .helpers import WeiboAPI, TwitterAPI
from .models import User


# Create your views here.

def home(request):
    user = request.user
    weibo = WeiboAPI()
    twitter = TwitterAPI()
    statuses = []
    if user.is_authenticated():
        if user.wei_id:
            data = weibo.get_user_timeline(user.wei_token)
            statuses.extend(weibo.extract_raw_status(data))
        if user.twi_id:
            data = twitter.get_user_timeline(user.twi_token, user.twi_token_secret)
            statuses.extend(twitter.extract_raw_statuses(data))
    else:
        data = weibo.get_pub_timeline(weibo.admin_token)
        statuses = weibo.extract_raw_status(data)
    statuses = sorted(statuses, key=lambda s: s.get('time'))
    context = {'statuses': statuses}
    return render(request, 'main/index.html', context=context)


def weibo_access_token(request):
    weibo = WeiboAPI()
    code = request.GET.get('code')
    data = weibo.access_token(code)
    token = data.get('access_token')
    expire = data.get('expires_in')
    wei_id = data.get('uid')

    User.objects.update_or_create(
        wei_id=wei_id,
        defaults={
            'wei_token': token,
            'wei_token_expire': timezone.now() + timedelta(0, int(expire) - 60),
            'username': str(int(time.time()))
        }
    )
    user = authenticate(wei_id=wei_id)
    login(request, user)

    return redirect('main:home')


def twitter_access_token(request):
    oauth_token = request.GET.get('oauth_token')
    oauth_verifier = request.GET.get('oauth_verifier')

    previous_oauth_token = request.session.get('oauth_token')
    if oauth_token == previous_oauth_token:
        twitter = TwitterAPI()
        data = twitter.access_token(oauth_token, oauth_verifier)
        token = data.get('oauth_token')
        token_secret = data.get('oauth_token_secret')
        twi_id = data.get('user_id')
        User.objects.update_or_create(
            twi_id=twi_id,
            defaults={
                'twi_token': token,
                'twi_token_secret': token_secret,
                'username': str(int(time.time()))
            }
        )
        user = authenticate(twi_id=twi_id)
        login(request, user)
        return redirect('main:home')


def site_login(request):
    site = request.GET.get('site', None)
    if site == 'weibo':
        weibo = WeiboAPI()
        return redirect(weibo.oauth2_url)

    elif site == 'twitter':
        twitter = TwitterAPI()
        oauth_token, oauth_token_secret = twitter.request_token()

        request.session['oauth_token'] = oauth_token
        request.session['oauth_token_secret'] = oauth_token_secret

        return redirect(twitter.get_authorize_url())

    return render(request, 'main/login.html')


def site_logout(request):
    user = request.user
    if user.is_authenticated:
        logout(request)

    return redirect(reverse('main:home'))
