from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.http import JsonResponse

from datetime import timedelta
import time

from .helpers import login_required
from .apis import WeiboAPI, TwitterAPI
from .models import User

from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

redis_publisher = RedisPublisher(facility='foobar', broadcast=True)


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
            user.wei_head = statuses[0]['id']
            user.wei_tail = statuses[-1]['id']
        if user.twi_id:
            data = twitter.get_user_timeline(user.twi_token, user.twi_token_secret)
            statuses.extend(twitter.extract_raw_statuses(data))
            user.twi_head = statuses[0]['id']
            user.twi_tail = statuses[-1]['id']
        user.save()
    elif weibo.admin_token:
        statuses.extend(
            weibo.extract_raw_status(weibo.get_pub_timeline(weibo.admin_token)))

    if statuses:
        statuses = sorted(statuses, key=lambda s: s.get('time'), reverse=True)
        context = {'statuses': statuses}
        return render(request, 'main/index.html', context=context)

    return redirect(reverse('main:site_login'))


def load_more(request):
    user = request.user
    message = RedisMessage(user.username + 'want more !')
    redis_publisher.publish_message(message)
    weibo = WeiboAPI()
    twitter = TwitterAPI()
    statuses = []
    if user.is_authenticated:
        if user.wei_id:
            data = weibo.get_user_timeline(user.wei_token, max_id=user.wei_tail)
            statuses.extend(weibo.extract_raw_status(data)[1:-1])
            user.wei_tail = statuses[-1]['id']
        if user.twi_id:
            data = twitter.get_user_timeline(user.twi_token, user.twi_token_secret, max_id=user.twi_tail)
            statuses.extend(twitter.extract_raw_statuses(data)[1:-1])
            user.twi_tail = statuses[-1]['id']
        user.save()
        statuses = sorted(statuses, key=lambda s: s.get('time'), reverse=True)
        return JsonResponse(
            {
                'status': 200,
                'msg': '',
                'content': statuses
            }
        )
    return JsonResponse(
        {
            'status': 400,
            'msg': '登陆后再使用该功能'
        }
    )


def load_new(request):
    pass


def weibo_access_token(request):
    weibo = WeiboAPI()
    code = request.GET.get('code')
    data = weibo.access_token(code)
    token = data.get('access_token')
    expire = data.get('expires_in')
    wei_id = data.get('uid')

    if request.session.get('action') == 'linkto':
        user = User.get_or_404(twi_id=request.user.twi_id)
        old_user = User.get(wei_id=wei_id)
        update_fields = {
            'wei_id': wei_id,
            'wei_token': token,
            'wei_token_expire': timezone.now() + timedelta(0, int(expire) - 60),
        }

        if old_user:
            User.merge_user(old_user, user, update_fields)
        else:
            user.update_fields(update_fields)
        return redirect(reverse('main:user_account'))

    else:
        u, c = User.objects.update_or_create(
            wei_id=wei_id,
            defaults={
                'wei_token': token,
                'wei_token_expire': timezone.now() + timedelta(0, int(expire) - 60),
            }
        )
        if not u.username:
            u.username = str(int(time.time()))
            u.save()
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

        if request.session.get('action') == 'linkto':
            user = User.get_or_404(wei_id=request.user.wei_id)
            old_user = User.get(twi_id=twi_id)
            update_fields = {
                'twi_id': twi_id,
                'twi_token': token,
                'twi_token_secret': token_secret
            }

            if old_user:
                User.merge_user(old_user, user, update_fields)
            else:
                user.update_fields(update_fields)
            return redirect(reverse('main:user_account'))

        else:
            u, c = User.objects.update_or_create(
                twi_id=twi_id,
                defaults={
                    'twi_token': token,
                    'twi_token_secret': token_secret,
                }
            )
            if not u.username:
                u.username = str(int(time.time()))
                u.save()
            user = authenticate(twi_id=twi_id)
            login(request, user)
            return redirect('main:home')
    return reverse('main:home')


def site_login(request):
    site = request.GET.get('site', None)
    request.session['action'] = request.GET.get('action', None)

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


@login_required
def user_account(request):
    return render(request, 'main/user/account.html')
