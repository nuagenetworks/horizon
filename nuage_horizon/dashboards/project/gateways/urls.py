from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.gateways import views as gw_views
from nuage_horizon.dashboards.project.gateways.ports import urls as port_urls


GATEWAY = r'^(?P<gateway_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^$', gw_views.IndexView.as_view(), name='index'),
    url(GATEWAY % '$', gw_views.DetailView.as_view(), name='detail'),
    url(r'^ports/', include(port_urls, namespace='ports')),)
