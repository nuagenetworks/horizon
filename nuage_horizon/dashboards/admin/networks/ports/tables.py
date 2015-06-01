# Copyright 2012 NEC Corporation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging

from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.admin.networks.ports \
    import tables as original
from nuage_horizon.dashboards.project.networks.ports \
    import tables as project_tables

LOG = logging.getLogger(__name__)


class PortsTable(original.PortsTable):
    class Meta(object):
        name = "ports"
        verbose_name = _("Ports")
        table_actions = (original.CreatePort,
                         project_tables.AddAllowedAddressPair,
                         original.DeletePort)
        row_actions = (original.UpdatePort,
                       project_tables.AddAllowedAddressPair,
                       original.DeletePort)
        hidden_title = False
