from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.application_services import views


APPLICATION_SERVICE = r'^(?P<application_service_id>[^/]+)/%s$'


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(APPLICATION_SERVICE % '$', views.IndexView.as_view(), name='detail'),
    url(APPLICATION_SERVICE % 'update', views.UpdateView.as_view(),
        name='update'),)
