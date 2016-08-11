# coding: utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap

from tastypie.api import Api

from note.feeds import LatestNoteFeed
from note.models import Note
from weixin.models import WeixinMp
from .views import ContactView, AboutView
from feedfish.api import FeedFishResource, PublicFishResource
from ninan.api import UserResource, UserInfoResource
from backends.views import TimelineListView
from xlink.api.resources import (DataPointResource,
                                 SensorResource,
                                 DeviceResource,
                                 CommandResource)

# APIs
v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(UserInfoResource())
v1_api.register(FeedFishResource())
v1_api.register(PublicFishResource())
v1_api.register(DataPointResource())
v1_api.register(SensorResource())
v1_api.register(DeviceResource())
v1_api.register(CommandResource())


admin.autodiscover()

handler500 = 'ninan.views.server_error'

urlpatterns = patterns(
    '',
    url(r'^$', TimelineListView.as_view(),
        name="home"),
    url(r'^note/', include('note.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^reminder/', include('reminder.urls')),
    url(r'^%s/' % settings.AMD_ROOT, include(admin.site.urls)),
    url(r'^feeds/note/$', LatestNoteFeed()),
    url(r'^about/$', AboutView.as_view()),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^test/$', 'ninan.views.test'),
    url(r'i18n/', include('django.conf.urls.i18n')),
    url(r'^weixin/', include('weixin.urls')),
    url(r'^milestone/', include('milestone.urls')),
    url(r'^feedfish/', include('feedfish.urls')),
    url(r'^social/', include('social.apps.django_app.urls',
        namespace='social')),
    url(r'email/$', 'ninan.views.require_email', name='require_email'),
    url(r'signup-email/', 'ninan.views.signup_email'),
    url(r'email-sent/', 'ninan.views.validation_sent'),
    url(r'done/$', 'ninan.views.done', name='done'),
    url(r'logout/$', 'ninan.views.logout', name='logout'),
    url(r'login/$', 'ninan.views.home', name='login'),
    url(r'^backends/', include('backends.urls')),
    url(r'^search/', include('haystack.urls')),
)

info_dict = {
    'queryset': Note.objects.filter(is_valid=True, is_private=False),
    'date_field': 'date_modified',
}

weixinmp_dict = {
    'queryset': WeixinMp.objects.filter(is_valid=True),
    'date_field': 'date_created',
}

site_maps = {
    'flatpages': FlatPageSitemap,
    'note': GenericSitemap(info_dict),
    'weixinmp': GenericSitemap(weixinmp_dict)
}

urlpatterns += patterns(
    '',
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': site_maps})
)

# APIs
urlpatterns += patterns(
    "",
    url('^api/', include(v1_api.urls)),
    url('^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
)
