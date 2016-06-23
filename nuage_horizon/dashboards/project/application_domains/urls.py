from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.application_domains import views


APPLICATION_DOMAIN = r'^(?P<app_domain_id>[^/]+)/%s$'


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(APPLICATION_DOMAIN % '$', views.DetailView.as_view(), name='detail'),
    url(APPLICATION_DOMAIN % 'update', views.UpdateView.as_view(),
        name='update'),
    url(APPLICATION_DOMAIN % 'applications/create',
        views.CreateApplicationView.as_view(), name='createApplication'),
    url(APPLICATION_DOMAIN % 'applications/(?P<application_id>[^/]+)/update',
        views.UpdateApplicationView.as_view(), name='updateApplication'),
)
