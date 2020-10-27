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

from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.networks.subnets \
    import tabs as original

from nuage_horizon.dashboards.project.networks.subnets \
    import tables as nuage_sub_tables


class SubnetsTab(original.SubnetsTab):
    table_classes = (nuage_sub_tables.NuageSubnetsTable,)

    def get_subnets_data(self):
        try:
            network_id = self.tab_group.kwargs['network_id']
            fields = ['name', 'id', 'cidr', 'ip_version', 'gateway_ip',
                      'vsd_managed']
            subnets = api.neutron.subnet_list(
                self.request, network_id=network_id, fields=fields)
        except Exception:
            subnets = []
            msg = _('Subnet list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return subnets


class OverviewTab(original.OverviewTab):
    template_name = "nuage/networks/subnets/_detail_overview.html"


original.SubnetDetailTabs.tabs = (OverviewTab,)
