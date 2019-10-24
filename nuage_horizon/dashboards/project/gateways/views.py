from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy
from horizon import exceptions
from horizon import tables
from horizon.utils import memoized

from nuage_horizon.api import neutron
from nuage_horizon.dashboards.project.gateways.ports \
    import tables as port_tables
from nuage_horizon.dashboards.project.gateways \
    import tables as gateway_tables


class IndexView(tables.DataTableView):
    table_class = gateway_tables.GatewaysTable
    template_name = 'nuage/gateways/index.html'

    def get_data(self):
        try:
            gws = neutron.nuage_gateway_list(self.request)
        except Exception:
            gws = []
            msg = _('Nuage Gateway list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return gws


class DetailView(tables.DataTableView):
    table_class = port_tables.PortsTable
    template_name = 'nuage/gateways/detail.html'
    page_title = _("Gateway Details: {{ gateway.name }}")
    failure_url = reverse_lazy('horizon:project:gateways:index')

    def get_data(self):
        try:
            gw = self._get_gateway_data()
            if gw:
                ports = neutron.nuage_gateway_port_list(self.request, gw.id)
            else:
                ports = []
        except Exception:
            ports = []
            msg = _('Nuage Gateway Port list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return ports

    @memoized.memoized_method
    def _get_gateway_data(self):
        try:
            gw_id = self.kwargs['gateway_id']
            gateway = neutron.nuage_gateway_get(self.request, gw_id)
        except Exception:
            gateway = None
            msg = _('Gateway can not be retrieved.')
            exceptions.handle(self.request, msg, redirect=self.failure_url)
        return gateway

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        gateway = self._get_gateway_data()
        context["gateway"] = gateway
        table = gateway_tables.GatewaysTable(self.request)
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(gateway)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:project:gateways:index')
