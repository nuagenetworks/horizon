from openstack_dashboard.dashboards.project.networks.subnets \
    import views as original

from nuage_horizon.dashboards.project.networks.subnets \
    import workflows as nuage_subnet_workflows


original.CreateView.workflow_class = nuage_subnet_workflows.CreateSubnet
original.CreateView.ajax_template_name = 'nuage/networks/create.html'
