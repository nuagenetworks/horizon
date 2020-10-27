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

from django import http
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from nuage_horizon.api import neutron
from nuage_horizon.dashboards.project.gateways.ports.vlans \
    import forms as vlan_forms
from nuage_horizon.dashboards.project.gateways.ports.vlans \
    import tables as gw_vlan_tables


class IndexView(tables.DataTableView):
    table_class = gw_vlan_tables.VlansTable
    template_name = 'nuage/gateways/ports/vlans/index.html'

    def get_data(self):
        request = self.request
        try:
            gw_vlans = neutron.nuage_gateway_vlan_list(request)
            vlans = []
            for vlan in gw_vlans:
                if vlan.get('vport'):
                    dict = vlan.to_dict()
                    vport = neutron.nuage_gateway_vport_get(request,
                                                            vlan['vport'])
                    dict['vport'] = vport
                    if vport:
                        subnet = neutron.subnet_get(request,
                                                    vport.get('subnet'))
                        dict['subnet'] = subnet
                        if vport.get('port'):
                            port = neutron.port_get(request,
                                                    vport['port'])
                            dict['port'] = port
                    vlan = neutron.NuageGatewayVlan(dict)
                vlans.append(vlan)
        except Exception:
            vlans = []
            msg = _('Nuage Gateway Vlanlist can not be retrieved.')
            exceptions.handle(self.request, msg)
        return vlans


class CreateView(forms.ModalFormView):
    form_class = vlan_forms.CreateForm
    form_id = "create_gw_vlan_form"
    modal_header = _("Create Gateway Vlan")
    template_name = 'nuage/gateways/ports/vlans/create.html'
    success_url = 'horizon:project:gateways:ports:detail'
    failure_url = 'horizon:project:gateways:ports:detail'
    submit_url = 'horizon:project:gateways:ports:createvlan'
    page_title = _("Create Gateway Vlan")
    submit_label = _("Create Port Vlan")

    def get_success_url(self):
        return reverse(self.success_url, args=(self.kwargs['gw_port_id'],))

    @memoized.memoized_method
    def _get_object(self):
        port_id = self.kwargs["gw_port_id"]
        try:
            return neutron.nuage_gateway_port_get(self.request, port_id)
        except Exception:
            redirect = reverse(self.failure_url, args=[port_id])
            msg = _("Unable to retrieve Gateway Port.")
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['gw_port'] = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(self._get_object().id,))
        return context

    def get_initial(self):
        gw_port = self._get_object()
        return {"gw_port_id": self.kwargs['gw_port_id'],
                "gw_port": gw_port}


class UpdateView(forms.ModalFormView):
    form_class = vlan_forms.UpdateForm
    form_id = "update_gw_vlan_form"
    modal_header = _("Update Gateway Vlan")
    template_name = 'nuage/gateways/ports/vlans/update.html'
    admin_success_url = 'horizon:project:gateways:ports:detail'
    user_success_url = 'horizon:project:gateways:ports:vlans:index'
    submit_url = 'horizon:project:gateways:ports:vlans:edit'
    page_title = _("Update Gateway Vlan")
    submit_label = _("Update")

    def get_success_url(self):
        if self.request.user.is_superuser:
            args = [self._get_object()['gatewayport']]
            return reverse(self.admin_success_url, args=args)
        else:
            return reverse(self.user_success_url)

    @memoized.memoized_method
    def _get_object(self):
        vlan_id = self.kwargs["gw_vlan_id"]
        try:
            return neutron.nuage_gateway_vlan_get(
                self.request, vlan_id)
        except Exception:
            msg = _("Unable to retrieve Gateway Vlan.")
            exceptions.handle(self.request, msg)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['gw_vlan'] = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(self._get_object().id,))
        return context

    def get_initial(self):
        gw_vlan = self._get_object()
        gw_port = neutron.nuage_gateway_port_get(
            self.request, gw_vlan.get('gatewayport'))
        gw_vport = None
        if gw_vlan.get('vport'):
            gw_vport = neutron.nuage_gateway_vport_get(
                self.request, gw_vlan['vport'])
        return {"gw_vlan_id": self.kwargs['gw_vlan_id'],
                "gw_port": gw_port,
                "vlan_range": gw_port['vlan'],
                "vlan": gw_vlan.get('value'),
                "assigned": gw_vlan.get('assigned'),
                "type": gw_vport.get('type').lower() if gw_vport else None,
                "subnet_id": gw_vport.get('subnet') if gw_vport else None,
                "port_id": gw_vport.get('port') if gw_vport else None}


def valid_gw_subnet(subnet, id_net):
    return (not subnet['vsd_managed']
            and not id_net[subnet['network_id']]['router:external'])


def subnet_data(request):
    tenant_id = request.GET.get('tenant_id', request.user.tenant_id)
    subnet_list = neutron.subnet_list(request, tenant_id=tenant_id)
    net_list = neutron.network_list(request)
    id_net = dict([(net.id, net) for net in net_list])
    subnet_list = [subnet.to_dict() for subnet in subnet_list
                   if valid_gw_subnet(subnet, id_net)]
    response = http.JsonResponse(subnet_list, safe=False)
    return response


def port_data(request):
    network_id = request.GET.get('network_id', None)
    port_list = neutron.port_list(request, network_id=network_id)

    port_list = [port.to_dict() for port in port_list
                 if (not port['device_id'])]
    response = http.JsonResponse(port_list, safe=False)
    return response
