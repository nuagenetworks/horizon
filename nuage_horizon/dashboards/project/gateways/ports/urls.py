from django.conf.urls import url
from django.conf.urls import include

from nuage_horizon.dashboards.project.gateways.ports \
    import views as gw_port_views
from nuage_horizon.dashboards.project.gateways.ports.vlans \
    import urls as vlan_urls
from nuage_horizon.dashboards.project.gateways.ports.vlans \
    import views as vlan_views

GW_PORT = r'^(?P<gw_port_id>[^/]+)/%s'


urlpatterns = [
    url(GW_PORT % '$', gw_port_views.DetailView.as_view(), name='detail'),
    url(GW_PORT % 'createvlan', vlan_views.CreateView.as_view(),
        name='createvlan'),
    url(r'^vlans/', include((vlan_urls, 'vlans'), namespace='vlans')),
]
