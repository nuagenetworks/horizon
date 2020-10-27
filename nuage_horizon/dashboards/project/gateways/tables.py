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

import logging

from django.utils.translation import ugettext_lazy as _
from horizon import tables


LOG = logging.getLogger(__name__)


class GatewaysTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:gateways:detail')
    description = tables.Column("description", verbose_name=_("Description"))
    type = tables.Column("type", verbose_name=_("Type"))
    status = tables.Column("status", verbose_name=_("Status"))
    system_id = tables.Column("systemid", verbose_name=_("System Id"))

    class Meta:
        name = "gateways"
        verbose_name = _("Gateways")
