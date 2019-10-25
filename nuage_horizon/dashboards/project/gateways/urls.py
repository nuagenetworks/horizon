from django.conf.urls import include
from django.conf.urls import url

from nuage_horizon.dashboards.project.gateways.ports import urls as port_urls
from nuage_horizon.dashboards.project.gateways import views as gw_views


GATEWAY = r'^(?P<gateway_id>[^/]+)/%s'


urlpatterns = [
    url(r'^$', gw_views.IndexView.as_view(), name='index'),
    url(GATEWAY % '$', gw_views.DetailView.as_view(), name='detail'),
    url(r'^ports/', include((port_urls, 'ports'), namespace='ports')),
]
