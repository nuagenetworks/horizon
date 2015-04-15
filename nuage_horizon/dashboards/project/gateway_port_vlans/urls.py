from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.gateway_port_vlans \
    import views as gw_port_vlan_views


gw_port_vlan = r'^(?P<gw_port_vlan_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^$', gw_port_vlan_views.IndexView.as_view(), name='index'),
    url(gw_port_vlan % '$', gw_port_vlan_views.UpdateView.as_view(),
        name='edit'),
    url(r'^listSubnets$', gw_port_vlan_views.subnetData, name='listsubnets'),
    url(r'^listPorts', gw_port_vlan_views.portData, name='listports'),
)
