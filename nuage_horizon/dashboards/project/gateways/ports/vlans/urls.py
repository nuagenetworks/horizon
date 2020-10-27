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

from django.conf.urls import url

from nuage_horizon.dashboards.project.gateways.ports.vlans \
    import views as gw_vlan_views

gw_vlan = r'^(?P<gw_vlan_id>[^/]+)/%s'


urlpatterns = [
    url(r'^$', gw_vlan_views.IndexView.as_view(), name='index'),
    url(gw_vlan % '$', gw_vlan_views.UpdateView.as_view(),
        name='edit'),
    url(r'^listSubnets$', gw_vlan_views.subnet_data, name='listsubnets'),
    url(r'^listPorts', gw_vlan_views.port_data, name='listports'),
]
