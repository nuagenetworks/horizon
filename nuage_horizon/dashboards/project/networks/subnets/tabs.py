from horizon import exceptions

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.networks.subnets \
    import tabs as def_tabs
from nuage_horizon.dashboards.project.networks.subnets \
    import tables as nuage_sub_tables


class SubnetsTab(def_tabs.SubnetsTab):
    table_classes = (nuage_sub_tables.NuageSubnetsTable,)

    def get_subnets_data(self):
        try:
            network_id = self.tab_group.kwargs['network_id']
            fields = ['name', 'id', 'cidr', 'ip_version', 'gateway_ip',
                      'vsd_managed']
            subnets = api.neutron.subnet_list(
                self.request, network_id=network_id, fields=fields)
        except Exception:
            subnets = []
            msg = _('Subnet list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return subnets


class OverviewTab(def_tabs.OverviewTab):
    template_name = "nuage/networks/subnets/_detail_overview.html"

def_tabs.SubnetDetailTabs.tabs = (OverviewTab,)
