from nuage_horizon.dashboards.project.networks.subnets import views as nuage_views
from nuage_horizon.dashboards.project.networks.subnets \
    import workflows as nuage_subnet_workflows


class CreateView(nuage_views.CreateView):
    workflow_class = nuage_subnet_workflows.CreateSubnet
    ajax_template_name = 'nuage/networks/create.html'


class UpdateView(nuage_views.UpdateView):
    workflow_class = nuage_subnet_workflows.UpdateSubnet
    ajax_template_name = 'nuage/networks/create.html'