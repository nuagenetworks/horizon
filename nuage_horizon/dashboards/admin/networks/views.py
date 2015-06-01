# Copyright 2015 Alcatel-Lucent USA Inc.
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

from openstack_dashboard.dashboards.project.networks import views as original

from nuage_horizon.dashboards.admin.networks.ports \
    import tables as nuage_port_tables
from nuage_horizon.dashboards.project.networks.subnets \
    import tables as nuage_sub_tables


class NuageDetailView(original.DetailView):
    table_classes = (nuage_sub_tables.NuageSubnetsTable,
                     nuage_port_tables.PortsTable)
