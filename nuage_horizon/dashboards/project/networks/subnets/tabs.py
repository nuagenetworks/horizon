from openstack_dashboard.dashboards.project.networks.subnets \
    import tabs as def_tabs


class OverviewTab(def_tabs.OverviewTab):
    template_name = "nuage/networks/subnets/_detail_overview.html"

def_tabs.SubnetDetailTabs.tabs = (OverviewTab,)
