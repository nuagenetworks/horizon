import logging

from nuage_horizon.api import neutron
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.project.networks import \
    workflows as net_workflows

from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon import base


LOG = logging.getLogger(__name__)


class CreateSubnetTypeAction(workflows.Action):
    with_subnet = forms.BooleanField(label=_("Create Subnet"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switchable',
                                         'data-slug': 'with_subnet',
                                         'data-hide-tabs': 'create_network__'
                                                           'createsubnetdetail'
                                                           'action '
                                                           'create_network__'
                                                           'createsubnetinfo'
                                                           'action',
                                         'data-hide-on-checked': 'false'
                                     }),
                                     initial=True,
                                     required=False)
    subnet_type = forms.ChoiceField(label=_("Subnet choice"),
                                    widget=forms.Select(attrs={
                                        'class': 'switched',
                                        'data-slug': 'nuage_id',
                                        'data-switch-on': 'with_subnet',
                                    }),
                                    help_text=_(
                                        "Optional Subnet ID from Nuage. "
                                        "This links the subnet to an "
                                        "existing Nuage one, making it "
                                        "VSD managed"),
                                    required=False)

    class Meta:
        name = _("Subnet Type")
        help_text = _('Chose the type of subnet you are about to create.')

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetTypeAction, self).__init__(request, context, *args,
                                                     **kwargs)
        if request.user.is_superuser:
            choices = [('os', _("OpenStack Managed Subnet")),
                       ('vsd_manual', _("VSD Managed Subnet (Manual)"))]
            subnet_choices = choices
            self.fields['subnet_type'].choices = subnet_choices


class CreateSubnetType(workflows.Step):
    action_class = CreateSubnetTypeAction
    contributes = ("with_subnet", "subnet_type")


class CreateSubnetInfoAction(net_workflows.CreateSubnetInfoAction):
    nuage_id = forms.CharField(max_length=255,
                               label=_("Nuage UUID"),
                               required=True,
                               initial='.')
    net_partition = forms.CharField(max_length=255,
                               label=_("Nuage Net Partition"),
                               required=True,
                               initial='.')

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetInfoAction, self).__init__(request, context, *args,
                                                     **kwargs)
        del self.fields['with_subnet']

    def clean(self):
        cleaned_data = super(workflows.Action, self) \
            .clean()
        if 'cidr' in cleaned_data.keys() \
                and cleaned_data['cidr']:
            self._check_subnet_data(cleaned_data)
        return cleaned_data

    def get_hidden_fields(self, context):
        hidden = True
        shown = False
        if context['subnet_type'] == 'os':
            return {'id_nuage_id': hidden,
                    'id_net_partition': hidden,
                    'subnet_name': shown,
                    'id_cidr': shown,
                    'id_ip_version': shown,
                    'id_gateway_ip': shown,
                    'id_no_gateway': shown}
        else:
            return {'id_nuage_id': shown,
                    'id_net_partition': shown,
                    'subnet_name': shown,
                    'id_cidr': hidden,
                    'id_ip_version': hidden,
                    'id_gateway_ip': hidden,
                    'id_no_gateway': hidden}

    def get_locked_fields(self, context, form_data):
        return self._get_locked_fields(False, form_data)

    def _get_locked_fields(self, locked, form_data):
        locked_fields = {'id_gateway_ip': locked,
                         'id_nuage_id': locked,
                         'id_net_partition': locked}
        if 'id_cidr' in form_data:
            locked_fields['id_cidr'] = locked and form_data['id_cidr']
            locked_fields['id_ip_version'] = locked and form_data['id_cidr']
        return locked_fields

    def get_form_data(self, context, request):
        if context['subnet_type'] == 'vsd_manual':
            return {'id_cidr': '',
                    'id_gateway_ip': '',
                    'id_subnet_name': '',
                    'id_nuage_id': '',
                    'id_net_partition': ''}
        else:
            return {'id_cidr': '',
                    'id_gateway_ip': '',
                    'id_subnet_name': '',
                    'id_nuage_id': '.',
                    'id_net_partition': '.'}

    class Meta:
        name = _("Subnet")
        help_text = _('Create a subnet associated with the new network, '
                      'in which case "Network Address" must be specified. '
                      'If you wish to create a network without a subnet, '
                      'uncheck the "Create Subnet" checkbox.')


class CreateSubnetInfo(workflows.Step):
    action_class = CreateSubnetInfoAction
    contributes = ("subnet_name", "cidr", "ip_version", "gateway_ip",
                   "no_gateway", "nuage_id", "net_partition")


class CreateSubnetDetailAction(net_workflows.CreateSubnetDetailAction):

    def get_hidden_fields(self, context):
        if context['subnet_type'] != 'os':
            return {'id_enable_dhcp': True}
        else:
            return {'id_enable_dhcp': False}

    class Meta:
        name = _("Subnet Details")
        help_text = _('Specify additional attributes for the subnet.')


class CreateSubnetDetail(net_workflows.CreateSubnetDetail):
    action_class = CreateSubnetDetailAction


class CreateNetwork(net_workflows.CreateNetwork):
    default_steps = (net_workflows.CreateNetworkInfo,
                     CreateSubnetType,
                     CreateSubnetInfo,
                     CreateSubnetDetail)

    def __init__(self, request=None, context_seed=None, entry_point=None, *args,
                 **kwargs):
        if not request.user.is_superuser:
            try:
                CreateNetwork.unregister(CreateSubnetType)
                CreateNetwork.unregister(CreateSubnetInfo)
                CreateNetwork.unregister(CreateSubnetDetail)
            except base.NotRegistered:
                pass
            self.default_steps = (net_workflows.CreateNetworkInfo,
                                  net_workflows.CreateSubnetInfo,
                                  net_workflows.CreateSubnetDetail)
        else:
            try:
                CreateNetwork.unregister(net_workflows.CreateSubnetInfo)
                CreateNetwork.unregister(net_workflows.CreateSubnetDetail)
            except base.NotRegistered:
                pass
        super(CreateNetwork, self).__init__(request, context_seed, entry_point,
                                            *args, **kwargs)

    def handle(self, request, data):
        network = self._create_network(request, data)
        if not network:
            return False

        if not data['with_subnet']:
            return True
        subnet = self._create_subnet(request, data, network, no_redirect=True)
        if subnet:
            return True
        else:
            self._delete_network(request, network)
            return False

    def _create_subnet(self, request, data, network=None, tenant_id=None,
                       no_redirect=False):
        if network:
            network_id = network.id
            network_name = network.name
        else:
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

            if tenant_id:
                params['tenant_id'] = tenant_id
            if data['no_gateway']:
                params['gateway_ip'] = None
            elif data['gateway_ip'] and data.get('subnet_type') == 'os':
                params['gateway_ip'] = data['gateway_ip']

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
            if no_redirect:
                redirect = None
            else:
                redirect = self.get_failure_url()
            exceptions.handle(request,
                              msg % {"sub": data['cidr'], "net": network_name,
                                     "reason": e},
                              redirect=redirect)
            return False

    @classmethod
    def _unregister(cls, step_class):
        pass