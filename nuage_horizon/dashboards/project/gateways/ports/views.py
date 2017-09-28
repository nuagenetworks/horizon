from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables
from horizon.utils import memoized

from nuage_horizon.api import neutron
from nuage_horizon.dashboards.project.gateways.ports.vlans import \
    tables as vlan_tables


class DetailView(tables.DataTableView):
    table_class = vlan_tables.VlansTable
    template_name = 'nuage/gateways/ports/detail.html'
    page_title = _("Gateway Port Details: {{ gw_port.name }}")
    failure_url = reverse_lazy('horizon:project:gateways:index')

    def get_data(self):
        request = self.request
        try:
            gw_port = self._get_gateway_port_data()
            gw_vlans = neutron.nuage_gateway_vlan_list(
                self.request, gw_port.id)
            vlans = []
            for vlan in gw_vlans:
                if vlan.get('vport'):
                    dict = vlan.to_dict()
                    vport = neutron.nuage_gateway_vport_get(request,
                                                            vlan['vport'])
                    dict['vport'] = vport
                    if vport and vport.get('subnet'):
                        subnet = neutron.subnet_get(request,
                                                    vport.get('subnet'))
                        dict['subnet'] = subnet
                        if vport.get('port'):
                            try:
                                port = neutron.port_get(request,
                                                        vport['port'])
                                dict['port'] = port
                            except Exception:
                                dict['port'] = None
                    vlan = neutron.NuageGatewayVlan(dict)
                vlans.append(vlan)
        except Exception:
            vlans = []
            msg = _('Nuage Gateway Vlan list can not be retrieved.')
            exceptions.handle(request, msg)
        return vlans

    @memoized.memoized_method
    def _get_gateway_port_data(self):
        try:
            gw_port_id = self.kwargs['gw_port_id']
            gw_port = neutron.nuage_gateway_port_get(self.request, gw_port_id)
        except Exception:
            gw_port = None
            msg = _('Gateway Port can not be retrieved.')
            exceptions.handle(self.request, msg, redirect=self.failure_url)
        return gw_port

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        gw_port = self._get_gateway_port_data()
        context["gw_port"] = gw_port
        context["url"] = self.get_redirect_url()
        return context

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:project:gateways:index')
