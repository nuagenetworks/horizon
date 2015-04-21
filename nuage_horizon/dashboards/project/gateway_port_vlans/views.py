import json

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django import http

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from nuage_horizon.api import neutron
from . import forms as vlan_forms
from . import tables as gw_port_vlan_tables


class IndexView(tables.DataTableView):
    table_class = gw_port_vlan_tables.VlansTable
    template_name = 'nuage/gateway_port_vlans/index.html'

    def get_data(self):
        request = self.request
        try:
            gw_port_vlans = neutron.nuage_gateway_port_vlan_list(request)
            vlans = []
            for vlan in gw_port_vlans:
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
                    vlan = neutron.NuageGatewayPortVlan(dict)
                vlans.append(vlan)
        except Exception:
            vlans = []
            msg = _('Nuage Gateway Port Vlanlist can not be retrieved.')
            exceptions.handle(self.request, msg)
        return vlans


class CreateView(forms.ModalFormView):
    form_class = vlan_forms.CreateForm
    form_id = "create_gw_port_vlan_form"
    modal_header = _("Create Gateway Port Vlan")
    template_name = 'nuage/gateway_port_vlans/create.html'
    success_url = 'horizon:project:gateways:ports:detail'
    failure_url = 'horizon:project:gateways:ports:detail'
    submit_url = 'horizon:project:gateways:ports:createvlan'
    page_title = _("Create Gateway Port Vlan")
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
    form_id = "update_gw_port_vlan_form"
    modal_header = _("Update Gateway Port Vlan")
    template_name = 'nuage/gateway_port_vlans/update.html'
    admin_success_url = 'horizon:project:gateways:ports:detail'
    user_success_url = 'horizon:project:gateway_port_vlans:index'
    submit_url = 'horizon:project:gateway_port_vlans:edit'
    page_title = _("Update Gateway Port Vlan")
    submit_label = _("Update")

    def get_success_url(self):
        if self.request.user.is_superuser:
            args = [self._get_object()['gatewayport']]
            return reverse(self.admin_success_url, args=args)
        else:
            return reverse(self.user_success_url)

    @memoized.memoized_method
    def _get_object(self):
        vlan_id = self.kwargs["gw_port_vlan_id"]
        try:
            return neutron.nuage_gateway_port_vlan_get(
                self.request, vlan_id)
        except Exception:
            msg = _("Unable to retrieve Gateway Port Vlan.")
            exceptions.handle(self.request, msg)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['gw_port_vlan'] = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(self._get_object().id,))
        return context

    def get_initial(self):
        gw_port_vlan = self._get_object()
        gw_port = neutron.nuage_gateway_port_get(
            self.request, gw_port_vlan.get('gatewayport'))
        gw_vport = None
        if gw_port_vlan.get('vport'):
            gw_vport = neutron.nuage_gateway_vport_get(
                self.request, gw_port_vlan['vport'])
        return {"gw_port_vlan_id": self.kwargs['gw_port_vlan_id'],
                "gw_port": gw_port,
                "vlan_range": gw_port['vlan'],
                "vlan": gw_port_vlan.get('value'),
                "tenant_id": gw_port_vlan.get('tenant'),
                "type": gw_vport.get('type').lower() if gw_vport else None,
                "subnet_id": gw_vport.get('subnet') if gw_vport else None,
                "port_id": gw_vport.get('port') if gw_vport else None}


def valid_gw_subnet(subnet, id_net):
    return (not subnet['vsd_managed']
            and not id_net[subnet['network_id']]['router:external'])


def subnetData(request):
    tenant_id = request.GET.get('tenant_id', request.user.tenant_id)
    subnet_list = neutron.subnet_list(request, tenant_id=tenant_id)
    net_list = neutron.network_list(request, tenant_id=tenant_id)
    id_net = dict([(net.id, net) for net in net_list])
    subnet_list = [subnet.to_dict() for subnet in subnet_list
                   if valid_gw_subnet(subnet, id_net)]
    response = http.HttpResponse(json.dumps(subnet_list, ensure_ascii=False))
    return response


def portData(request):
    network_id = request.GET.get('network_id', None)
    port_list = neutron.port_list(request, network_id=network_id)

    port_list = [port.to_dict() for port in port_list
                 if (not port['device_owner'] and not port['device_id']) ]
    response = http.HttpResponse(json.dumps(port_list, ensure_ascii=False))
    return response