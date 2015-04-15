from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.gateways.ports \
    import views as gw_port_views
from nuage_horizon.dashboards.project.gateway_port_vlans \
    import views as vlan_views

GW_PORT = r'^(?P<gw_port_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(GW_PORT % '$', gw_port_views.DetailView.as_view(), name='detail'),
    url(GW_PORT % 'createvlan', vlan_views.CreateView.as_view(),
        name='createvlan'),
)
