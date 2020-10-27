# Copyright 2020 Nokia.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from django.conf.urls import include
from django.conf.urls import url

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
