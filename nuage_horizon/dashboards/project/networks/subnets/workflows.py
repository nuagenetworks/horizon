import logging

from django.utils.translation import ugettext_lazy as _
from horizon import base
from horizon import exceptions
from horizon import workflows
from openstack_dashboard.dashboards.project.networks.subnets import workflows \
    as original
from openstack_dashboard.dashboards.project.networks import workflows \
    as network_workflows

from nuage_horizon.api import neutron
from nuage_horizon.dashboards.project.networks import workflows \
    as nuage_net_workflows


LOG = logging.getLogger(__name__)


class CreateSubnetTypeAction(nuage_net_workflows.CreateSubnetTypeAction):

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetTypeAction, self).__init__(request, context, *args,
                                                     **kwargs)
        del self.fields['with_subnet']

    class Meta:
        name = _("Subnet Type")
        help_text = _('Choose the type of subnet you are about to create.')


class CreateSubnetType(workflows.Step):
    action_class = CreateSubnetTypeAction
    contributes = ("with_subnet", "subnet_type", "org_id", "zone_id", "sub_id",
                   "hidden_org", "hidden_dom", "hidden_zone", "hidden_sub",
                   "hidden_ip_version_", "hidden_gateway_")


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


class CreateSubnet(original.CreateSubnet):
    default_steps = (CreateSubnetType,
                     CreateSubnetInfo,
                     nuage_net_workflows.CreateSubnetDetail)

    def __init__(self, request=None, context_seed=None, entry_point=None,
                 *args, **kwargs):
        if not request.user.is_superuser:
            try:
                CreateSubnet.unregister(CreateSubnetType)
                CreateSubnet.unregister(CreateSubnetInfo)
            except base.NotRegistered:
                pass
            self.default_steps = (original.CreateSubnetInfo,
                                  network_workflows.CreateSubnetDetail)
        else:
            try:
                CreateSubnet.unregister(original.CreateSubnetInfo)
            except base.NotRegistered:
                pass

        super(CreateSubnet, self).__init__(request, context_seed, entry_point,
                                           *args, **kwargs)

    @classmethod
    def _unregister(cls, step_class):
        pass

    def handle(self, request, data):
        network_id = self.context.get('network_id')
        try:
            params = {'network_id': network_id,
                      'name': data['subnet_name'],
                      'cidr': data['cidr'],
                      'ip_version': int(data['ip_version']),
                      'enable_dhcp': data['enable_dhcp']}
            if request.user.is_superuser and data.get('subnet_type') != 'os':
                params['nuagenet'] = data['nuage_id']
                params['net_partition'] = data['net_partition']
            if (request.user.is_superuser and data.get('underlay')
                    and data.get('underlay') != 'default'):
                params['underlay'] = data['underlay']

            params['gateway_ip'] = (
                None if data['no_gateway'] else data['gateway_ip'])

            self._setup_subnet_parameters(params, data)

            subnet = neutron.subnet_create(request, **params)
            self.context['subnet_id'] = subnet.id
            if 'vsd_subnet' in request.session.keys():
                del request.session['vsd_subnet']
            msg = _('Subnet "%s" was successfully created.') % data['cidr']
            LOG.debug(msg)
            return subnet
        except Exception as e:
            msg = _('Failed to create subnet "%(sub)s" for network "%(net)s": '
                    ' %(reason)s')
            redirect = self.get_failure_url()
            exceptions.handle(request,
                              msg % {"sub": data['cidr'], "net": network_id,
                                     "reason": e},
                              redirect=redirect)
            return False
