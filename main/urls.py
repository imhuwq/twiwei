from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^oauth2/weibo/access_token/$', view=views.weibo_access_token, name='weibo_access_token'),
    url(r'^oauth2/twitter/access_token/$', view=views.twitter_access_token, name='twitter_access_token'),
    url(r'^user/login/$', view=views.site_login, name='site_login'),
    url(r'^user/logout/$', view=views.site_logout, name='site_logout'),
    url(r'^$', view=views.home, name='home')
]
