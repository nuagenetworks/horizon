import logging

from horizon import workflows
from horizon import base
from horizon import forms
from horizon import exceptions

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from nuage_horizon.api import neutron
from nuage_horizon.dashboards.project.networks import workflows \
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
    contributes = ("with_subnet", "subnet_type", "sub_id", "org_id",)


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
                     nuage_net_workflows.CreateSubnetDetail)

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

    def handle(self, request, data):
        network_id = self.context.get('network_id')
        network_name = self.context.get('network_name')
        try:
            if data.get('subnet_type') == 'vsd_manual':
                vsd_subnet = neutron.vsd_subnet_get(request,
                                                    data['nuage_id'])
                data['cidr'] = vsd_subnet['cidr']
                data['ip_version'] = vsd_subnet['ip_version'][-1]
                data['gateway_ip'] = vsd_subnet['gateway']
            params = {'network_id': network_id,
                      'name': data['subnet_name'],
                      'cidr': data['cidr'],
                      'ip_version': int(data['ip_version'])}
            if request.user.is_superuser and data.get('subnet_type') != 'os':
                params['nuagenet'] = data['nuage_id']
                params['net_partition'] = data['net_partition']
            if (request.user.is_superuser and data.get('underlay')
                    and data.get('underlay') != 'default'):
                params['underlay'] = data['underlay']

            if data['no_gateway']:
                params['gateway_ip'] = None
            elif data['gateway_ip'] and data.get('subnet_type') == 'os':
                params['gateway_ip'] = data['gateway_ip']

            if data.get('subnet_type') != 'os' and vsd_subnet:
                data['enable_dhcp'] = vsd_subnet.get('cidr') is not None
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
                              msg % {"sub": data['cidr'], "net": network_name,
                                     "reason": e},
                              redirect=redirect)
            return False


class UpdateSubnetInfo(nuage_net_workflows.CreateSubnetInfo):
    action_class = subnet_workflows.UpdateSubnetInfoAction
    depends_on = ("network_id", "subnet_id")


class UpdateSubnetDetailAction(subnet_workflows.UpdateSubnetDetailAction):
    underlay = forms.ChoiceField(label=_("Underlay"),
                                 choices=[('default', _('Default')),
                                          ('true', _('True')),
                                          ('false', _('False'))])

    def __init__(self, request, context, *args, **kwargs):
        super(UpdateSubnetDetailAction, self).__init__(request, context, *args,
                                                       **kwargs)
        if not request.user.is_superuser or not context.get('network_id'):
            del self.fields['underlay']
        else:
            network = neutron.network_get(request, context['network_id'])
            if not network or not network.get('router:external', False):
                del self.fields['underlay']

    class Meta:
        name = _("Subnet")
        help_text = _('Create a subnet associated with the new network.')


class UpdateSubnetDetail(subnet_workflows.UpdateSubnetDetail):
    action_class = UpdateSubnetDetailAction
    contributes = ("enable_dhcp", "ipv6_modes", "allocation_pools",
                   "dns_nameservers", "host_routes", "underlay")


class UpdateSubnet(subnet_workflows.UpdateSubnet):
    default_steps = (UpdateSubnetInfo,
                     UpdateSubnetDetail)

    def _update_subnet(self, request, data):
        network_id = self.context.get('network_id')
        try:
            subnet_id = self.context.get('subnet_id')
            params = {}
            params['name'] = data['subnet_name']
            if data['no_gateway']:
                params['gateway_ip'] = None
            elif data['gateway_ip']:
                params['gateway_ip'] = data['gateway_ip']

            # We should send gateway_ip only when it is changed, because
            # updating gateway_ip is prohibited when the ip is used.
            # See bug 1227268.
            subnet = neutron.subnet_get(request, subnet_id)
            if params['gateway_ip'] == subnet.gateway_ip:
                del params['gateway_ip']
            if request.user.is_superuser and data.get('underlay') != 'default':
                params['underlay'] = data['underlay']

            self._setup_subnet_parameters(params, data, is_create=False)

            subnet = neutron.subnet_update(request, subnet_id, **params)
            msg = _('Subnet "%s" was successfully updated.') % data['cidr']
            LOG.debug(msg)
            return subnet
        except Exception as e:
            msg = (_('Failed to update subnet "%(sub)s": '
                     ' %(reason)s') %
                   {"sub": data['cidr'], "reason": e})
            redirect = reverse(self.failure_url, args=(network_id,))
            exceptions.handle(request, msg, redirect=redirect)
            return False
