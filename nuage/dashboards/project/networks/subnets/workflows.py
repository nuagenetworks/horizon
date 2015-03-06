import logging

from horizon import workflows
from horizon import base
from django.utils.translation import ugettext_lazy as _
from nuage.dashboards.project.networks import workflows \
    as nuage_net_workflows
from openstack_dashboard.dashboards.project.networks import workflows \
    as network_workflows
from openstack_dashboard.dashboards.project.networks.subnets import workflows \
    as subnet_workflows


LOG = logging.getLogger(__name__)


class CreateSubnetTypeAction(nuage_net_workflows.CreateSubnetTypeAction):

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetTypeAction, self).__init__(request, context, *args,
                                                     **kwargs)
        del self.fields['with_subnet']

    class Meta:
        name = _("Subnet Type")
        help_text = _('Chose the type of subnet you are about to create.')


class CreateSubnetType(workflows.Step):
    action_class = CreateSubnetTypeAction
    contributes = ("subnet_type",)


class CreateSubnetInfoAction(nuage_net_workflows.CreateSubnetInfoAction):

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetInfoAction, self).__init__(request, context, *args,
                                                     **kwargs)

    class Meta:
        name = _("Subnet")
        help_text = _('Create a subnet associated with the new network.')


class CreateSubnetInfo(workflows.Step):
    action_class = CreateSubnetInfoAction
    contributes = ("subnet_name", "cidr", "ip_version", "gateway_ip",
                   "no_gateway", "nuage_id", "net_partition")
    depends_on = ("network_id",)


class CreateSubnet(subnet_workflows.CreateSubnet):
    default_steps = (CreateSubnetType,
                     CreateSubnetInfo,
                     network_workflows.CreateSubnetDetail)

    def __init__(self, request=None, context_seed=None, entry_point=None, *args,
                 **kwargs):
        if not request.user.is_superuser:
            try:
                CreateSubnet.unregister(CreateSubnetType)
                CreateSubnet.unregister(CreateSubnetInfo)
            except base.NotRegistered:
                pass
            self.default_steps = (subnet_workflows.CreateSubnetInfo,
                                  network_workflows.CreateSubnetDetail)
        else:
            try:
                CreateSubnet.unregister(subnet_workflows.CreateSubnetInfo)
            except base.NotRegistered:
                pass

        super(CreateSubnet, self).__init__(request, context_seed, entry_point,
                                           *args, **kwargs)

    @classmethod
    def _unregister(cls, step_class):
        pass


class UpdateSubnetInfo(nuage_net_workflows.CreateSubnetInfo):
    action_class = subnet_workflows.UpdateSubnetInfoAction
    depends_on = ("network_id", "subnet_id")


class UpdateSubnet(subnet_workflows.UpdateSubnet):
    default_steps = (UpdateSubnetInfo,
                     subnet_workflows.UpdateSubnetDetail)
