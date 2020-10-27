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
from horizon import tables
from openstack_dashboard.dashboards.project.networks.subnets import \
    tables as original


class NuageSubnetsTable(original.SubnetsTable):
    vsd_managed = tables.Column("vsd_managed",
                                verbose_name=_("VSD Managed"))

    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(NuageSubnetsTable, self).__init__(request, data,
                                                needs_form_wrapper, **kwargs)
        if not request.user.is_superuser:
            del self.columns['vsd_managed']

    class Meta(original.SubnetsTable.Meta):
        pass
