# Copyright 2018 NOKIA
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

from horizon import tables
from openstack_dashboard.dashboards.project.access_and_security\
    .security_groups import tables as original


LOG = logging.getLogger(__name__)


class NuageSecurityGroupsTable(original.SecurityGroupsTable):
    stateful = tables.Column("stateful", verbose_name=_("Stateful"))

    class Meta(original.SecurityGroupsTable.Meta):
        pass
