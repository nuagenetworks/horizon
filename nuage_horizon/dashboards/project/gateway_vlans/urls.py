from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.gateway_vlans \
    import views as gw_vlan_views


gw_vlan = r'^(?P<gw_vlan_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^$', gw_vlan_views.IndexView.as_view(), name='index'),
    url(gw_vlan % '$', gw_vlan_views.UpdateView.as_view(),
        name='edit'),
    url(r'^listSubnets$', gw_vlan_views.subnet_data, name='listsubnets'),
    url(r'^listPorts', gw_vlan_views.port_data, name='listports'),
)
