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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms as horizon_forms
from horizon import tables as horizon_tables
from horizon.utils import memoized
from openstack_dashboard.api.neutron import NeutronAPIDictWrapper
from openstack_dashboard.dashboards.project.networks.ports \
    import tables as project_tables

from nuage_horizon.dashboards.project.networks.ports import forms
from nuage_horizon.dashboards.project.networks.ports import tables
from nuage_horizon.api import neutron

STATE_DICT = dict(project_tables.DISPLAY_CHOICES)
STATUS_DICT = dict(project_tables.STATUS_DISPLAY_CHOICES)


class DetailView(horizon_tables.DataTableView):
    table_class = tables.AllowedAddressPairsTable
    template_name = 'nuage/networks/ports/detail.html'
    page_title = _("Port details")

    def get_data(self):
        port = self._get_data()
        pairs = port.get('allowed_address_pairs', [])
        for pair in pairs:
            pair['id'] = pair['ip_address']
        return [NeutronAPIDictWrapper(pair) for pair in pairs]

    @memoized.memoized_method
    def _get_data(self):
        port_id = self.kwargs['port_id']

        try:
            port = neutron.port_get(self.request, port_id)
            port.admin_state_label = STATE_DICT.get(port.admin_state,
                                                    port.admin_state)
            port.status_label = STATUS_DICT.get(port.status,
                                                port.status)
        except Exception:
            port = []
            redirect = self.get_redirect_url()
            msg = _('Unable to retrieve port details.')
            exceptions.handle(self.request, msg, redirect=redirect)

        if (neutron.is_extension_supported(self.request, 'mac-learning')
                and not hasattr(port, 'mac_state')):
            port.mac_state = neutron.OFF_STATE

        return port

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        port = self._get_data()
        table = tables.PortsTable(self.request, network_id=port.network_id)
        context["port"] = port
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(port)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse('horizon:project:networks:index')


class AddAllowedAddressPair(horizon_forms.ModalFormView):
    form_class = forms.AddAllowedAddressPairForm
    form_id = "addallowedaddresspair_form"
    modal_header = _("Add allowed address pair")
    template_name = 'nuage/networks/ports/addresspair.html'
    context_object_name = 'port'
    submit_label = _("Submit")
    submit_url = "horizon:project:networks:ports:addallowedaddresspairs"
    success_url = 'horizon:project:networks:ports:detail'
    page_title = _("Add allowed address pair")

    def get_success_url(self):
        return reverse(self.success_url, args=(self.kwargs['port_id'],))

    def get_context_data(self, **kwargs):
        context = super(AddAllowedAddressPair, self).get_context_data(**kwargs)
        context["port_id"] = self.kwargs['port_id']
        context['submit_url'] = reverse(self.submit_url,
                                        args=(self.kwargs['port_id'],))
        port = neutron.port_get(self.request, context['port_id'])
        subnet_id = port['fixed_ips'][0]['subnet_id']
        context['subnet'] = neutron.subnet_get(self.request, subnet_id)
        return context

    def get_initial(self):
        return {'port_id': self.kwargs['port_id']}

