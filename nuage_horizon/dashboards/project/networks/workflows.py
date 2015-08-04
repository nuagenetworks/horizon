import logging

from nuage_horizon.api import neutron
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.project.networks import \
    workflows as net_workflows

from horizon import exceptions
from horizon import forms
from horizon import workflows
from horizon import base


LOG = logging.getLogger(__name__)


class UnsafeChoiceField(forms.ChoiceField):
    """
    This is an extension of the default choicefield with the exception that it
    will not validate that the value in the POST request matches the value
    during rendering of the Choicefield (In case Javascript alters the values
    client-side)
    """
    def validate(self, value):
        pass


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
    subnet_type = forms.ChoiceField(label=_("Subnet type choice"),
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
    org_id = UnsafeChoiceField(label=_("Organisation choice"),
                               required=False)
    dom_id = UnsafeChoiceField(label=_("Domain choice"),
                               required=False)
    zone_id = UnsafeChoiceField(label=_("Zone choice"),
                                required=False)
    sub_id = UnsafeChoiceField(label=_("Subnet choice"),
                               required=False)
    hidden_org = forms.CharField(widget=forms.HiddenInput,
                                 required=False)
    hidden_dom = forms.CharField(widget=forms.HiddenInput,
                                 required=False)
    hidden_zone = forms.CharField(widget=forms.HiddenInput,
                                  required=False)
    hidden_sub = forms.CharField(widget=forms.HiddenInput,
                                 required=False)

    class Meta:
        name = _("Subnet Type")
        help_text = _('Chose the type of subnet you are about to create.')

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetTypeAction, self).__init__(request, context, *args,
                                                     **kwargs)
        if request.user.is_superuser:
            self.fields['org_id'].choices = [('', _("Chose an Organization"))]
            self.fields['dom_id'].choices = [('', _("Chose a Domain"))]
            self.fields['zone_id'].choices = [('', _("Chose a Zone"))]
            self.fields['sub_id'].choices = [('', _("Chose a Subnet"))]

            type_choices = [('', _("Chose a subnet type")),
                            ('os', _("OpenStack Managed Subnet")),
                            ('vsd_manual', _("VSD Managed Subnet (Manual)")),
                            ('vsd_auto', _("VSD Managed Subnet (Auto)"))]
            self.fields['subnet_type'].choices = type_choices

    def _org_to_choices(self, organisations):
        choices = []
        for org in organisations:
            display_name = '(' + org['id'][:6] + ') ' + org['name']
            choices.append((org['id'], display_name))
        return choices

    def is_valid(self):
        valid = super(CreateSubnetTypeAction, self).is_valid()
        if not self.request.user.is_superuser:
            return valid
        if self.data['subnet_type'] == 'vsd_auto':
            if not self.data['hidden_sub']:
                self._errors['__all__'] = self.error_class(
                    ['A subnet must be selected below.'])
                valid = False
        if ((self.data.get('with_subnet') or self.initial.get('network_id'))
                and not self.data['subnet_type']):
            self._errors['subnet_type'] = self.error_class(
                ['This is a required field.'])
            valid = False

        return valid


class CreateSubnetType(workflows.Step):
    action_class = CreateSubnetTypeAction
    contributes = ("with_subnet", "subnet_type", "org_id", "zone_id", "sub_id",
                   "hidden_org", "hidden_dom", "hidden_zone", "hidden_sub")


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
        elif context['subnet_type'] == 'vsd_manual':
            return {'id_nuage_id': shown,
                    'id_net_partition': shown,
                    'subnet_name': shown,
                    'id_cidr': hidden,
                    'id_ip_version': hidden,
                    'id_gateway_ip': hidden,
                    'id_no_gateway': hidden}
        else:
            return {'id_nuage_id': shown,
                    'id_net_partition': shown,
                    'subnet_name': shown,
                    'id_cidr': shown,
                    'id_ip_version': shown,
                    'id_gateway_ip': hidden,
                    'id_no_gateway': hidden}

    def get_locked_fields(self, context, form_data):
        if context['subnet_type'] != 'vsd_manual' \
                and context['subnet_type'] != 'os':
            return self._get_locked_fields(True, form_data)
        else:
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
        elif context['subnet_type'] == 'os':
            return {'id_cidr': '',
                    'id_gateway_ip': '',
                    'id_subnet_name': '',
                    'id_nuage_id': '.',
                    'id_net_partition': '.'}
        else:
            if not context['sub_id']:
                return {}
            vsd_subnet = neutron.vsd_subnet_get(request, context['sub_id'])
            vsd_organisation = neutron.vsd_organisation_list(
                request, id=context['org_id'])[0]
            request.session['vsd_subnet'] = vsd_subnet
            request.session['vsd_organisation'] = vsd_organisation
            return {'id_nuage_id': vsd_subnet['id'],
                    'id_net_partition': vsd_organisation['name'],
                    'id_cidr': vsd_subnet['cidr'],
                    'id_gateway_ip': vsd_subnet['gateway'],
                    'id_ip_version': vsd_subnet['ip_version'][-1],
                    'id_subnet_name': vsd_subnet['name']}

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
    underlay = forms.ChoiceField(label=_("Underlay"),
                                 choices=[('default', _('Default')),
                                          ('true', _('True')),
                                          ('false', _('False'))])
    dummy_cidr = forms.IPField(label=_("Network Address"),
                               initial="",
                               help_text=_("OS requires a cidr. Fill in dummy "
                                           "value."),
                               version=forms.IPv4 | forms.IPv6,
                               mask=True)

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetDetailAction, self).__init__(request, context, *args,
                                                       **kwargs)
        if context.get('nuage_id') and context['nuage_id'] != ".":
            vsd_subnet = neutron.vsd_subnet_get(request, context['nuage_id'])
            request.session['vsd_subnet'] = vsd_subnet
            if vsd_subnet.get('cidr'):
                del self.fields['dummy_cidr']

        if not request.user.is_superuser or not context.get('network_id'):
            del self.fields['underlay']
        else:
            network = neutron.network_get(request, context['network_id'])
            if not network or not network.get('router:external', False):
                del self.fields['underlay']

    def get_hidden_fields(self, context):
        vsd_subnet = self.request.session.get('vsd_subnet')
        hidden = {'id_enable_dhcp': context['subnet_type'] != 'os'}
        if vsd_subnet:
            hidden['id_dummy_cidr'] = len(vsd_subnet.get('cidr')) > 0
        return hidden

    class Meta:
        name = _("Subnet Details")
        help_text = _('Specify additional attributes for the subnet.')


class CreateSubnetDetail(net_workflows.CreateSubnetDetail):
    action_class = CreateSubnetDetailAction
    contributes = ("enable_dhcp", "ipv6_modes", "allocation_pools",
                   "dns_nameservers", "host_routes", "underlay", "dummy_cidr")


class CreateNetwork(net_workflows.CreateNetwork):
    default_steps = (net_workflows.CreateNetworkInfo,
                     CreateSubnetType,
                     CreateSubnetInfo,
                     CreateSubnetDetail)

    def __init__(self, request=None, context_seed=None, entry_point=None,
                 *args, **kwargs):
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
                vsd_subnet = request.session.get('vsd_subnet')
                data['cidr'] = vsd_subnet['cidr'] or data['dummy_cidr']
                data['ip_version'] = vsd_subnet['ip_version'][-1]
                data['gateway_ip'] = vsd_subnet['gateway']
                request.session['vsd_subnet'] = vsd_subnet
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

            if tenant_id:
                params['tenant_id'] = tenant_id
            if data['no_gateway']:
                params['gateway_ip'] = None
            elif data['gateway_ip'] and data.get('subnet_type') == 'os':
                params['gateway_ip'] = data['gateway_ip']

            vsd_subnet = request.session.get('vsd_subnet')
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
