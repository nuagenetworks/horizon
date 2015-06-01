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

from django.core.urlresolvers import reverse

from nuage_horizon.dashboards.admin.networks.ports import tables
from nuage_horizon.dashboards.project.networks.ports \
    import views as project_views


class DetailView(project_views.DetailView):
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        port = context["port"]
        table = tables.PortsTable(self.request, network_id=port.network_id)
        context["actions"] = table.render_row_actions(port)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:admin:networks:index')
