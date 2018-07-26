import logging

from django.utils.translation import ugettext_lazy as _
from horizon import base
from horizon import exceptions
from horizon import forms
from horizon import workflows
from openstack_dashboard.dashboards.project.networks import \
    workflows as original

from nuage_horizon.api import neutron

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
    ip_version_ = UnsafeChoiceField(label=_("Cidr choice"),
                                    required=False)
    hidden_org = forms.CharField(widget=forms.HiddenInput,
                                 required=False)
    hidden_dom = forms.CharField(widget=forms.HiddenInput,
                                 required=False)
    hidden_zone = forms.CharField(widget=forms.HiddenInput,
                                  required=False)
    hidden_sub = forms.CharField(widget=forms.HiddenInput,
                                 required=False)
    hidden_ip_version_ = forms.CharField(widget=forms.HiddenInput,
                                         required=False)
    hidden_gateway_ = forms.CharField(widget=forms.HiddenInput,
                                      required=False)

    class Meta:
        name = _("Subnet Type")
        help_text = _('Choose the type of subnet you are about to create.')

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetTypeAction, self).__init__(request, context, *args,
                                                     **kwargs)
        if request.user.is_superuser:
            self.fields['org_id'].choices = [('', _("Choose an Organization"))]
            self.fields['dom_id'].choices = [('', _("Choose a Domain"))]
            self.fields['zone_id'].choices = [('', _("Choose a Zone"))]
            self.fields['sub_id'].choices = [('', _("Choose a Subnet"))]
            self.fields['ip_version_'].choices = [('', _("Choose a cidr"))]

            type_choices = [('os', _("OpenStack Managed Subnet")),
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
                   "hidden_org", "hidden_dom", "hidden_zone", "hidden_sub",
                   "hidden_ip_version_", "hidden_gateway_")


class CreateSubnetInfoAction(original.CreateSubnetInfoAction):
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
        if 'with_subnet' in self.fields:
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
                    'id_cidr': shown,
                    'id_ip_version': shown,
                    'id_gateway_ip': shown,
                    'id_no_gateway': shown}
        else:
            return {'id_nuage_id': shown,
                    'id_net_partition': shown,
                    'subnet_name': shown,
                    'id_cidr': shown,
                    'id_ip_version': shown,
                    'id_gateway_ip': shown if context['hidden_gateway_'] else hidden,
                    'id_no_gateway': shown,
                    'address_source': context['enable_dhcp']}  # managed

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
            locked_fields['id_gateway_ip'] = locked and form_data['id_cidr']
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

            if not self.data['ip_version_']:
                ip_version = '4'
            else:
                ip_version = self.data['ip_version_']

            if str(ip_version) == '4':
                cidr = vsd_subnet['cidr']
            else:
                cidr = vsd_subnet['ipv6_cidr']

            return {'id_nuage_id': vsd_subnet['id'],
                    'id_net_partition': vsd_organisation['name'],
                    'id_cidr': cidr,
                    'id_gateway_ip': context['hidden_gateway_'],
                    'id_ip_version': ip_version,
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


class CreateSubnetDetailAction(original.CreateSubnetDetailAction):
    underlay = forms.ChoiceField(label=_("Underlay"),
                                 choices=[('default', _('Default')),
                                          ('true', _('True')),
                                          ('false', _('False'))])

    def __init__(self, request, context, *args, **kwargs):
        super(CreateSubnetDetailAction, self).__init__(request, context, *args,
                                                       **kwargs)
        if context.get('nuage_id') and context['nuage_id'] != ".":
            try:
                vsd_subnet = neutron.vsd_subnet_get(request, context['nuage_id'])
            except Exception as e:
                msg = "Failed to find Nuage UUID {} on VSD"\
                    .format(context['nuage_id'])
                exceptions.handle(request, msg, redirect=False)
            else:
                request.session['vsd_subnet'] = vsd_subnet

        if not request.user.is_superuser or not context.get('network_id'):
            del self.fields['underlay']
        else:
            network = neutron.network_get(request, context['network_id'])
            if not network or not network.get('router:external', False):
                del self.fields['underlay']

    def get_hidden_fields(self, context):
        hidden = {'id_enable_dhcp': False,
                  'id_ipv6_modes': True}
        return hidden

    class Meta:
        name = _("Subnet Details")
        help_text = _('Specify additional attributes for the subnet.')


class CreateSubnetDetail(original.CreateSubnetDetail):
    action_class = CreateSubnetDetailAction
    contributes = ("enable_dhcp", "ipv6_modes", "allocation_pools",
                   "dns_nameservers", "host_routes", "underlay")


class CreateNetworkInfoAction(original.CreateNetworkInfoAction):
    with_subnet = forms.BooleanField(label=_("Create Subnet"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switchable',
                                         'data-slug': 'with_subnet',
                                         'data-hide-tab': 'create_network__'
                                                          'createsubnetinfo'
                                                          'action,'
                                                          'create_network__'
                                                          'createsubnetdetail'
                                                          'action,'
                                                          'create_network__'
                                                          'createsubnettype'
                                                          'action',
                                         'data-hide-on-checked': 'false'
                                     }),
                                     initial=True,
                                     required=False)

    class Meta(object):
        name = _("Network")
        help_text = _('Create a new network. '
                      'In addition, a subnet associated with the network '
                      'can be created in the following steps of this wizard.')


class CreateNetworkInfo(original.CreateNetworkInfo):
    action_class = CreateNetworkInfoAction


class CreateNetwork(original.CreateNetwork):

    def __init__(self, request=None, context_seed=None, entry_point=None,
                 *args, **kwargs):
        if not request.user.is_superuser:
            try:
                CreateNetwork.unregister(CreateNetworkInfo)
                CreateNetwork.unregister(CreateSubnetType)
                CreateNetwork.unregister(CreateSubnetInfo)
                CreateNetwork.unregister(CreateSubnetDetail)
            except base.NotRegistered:
                pass
            self.default_steps = (original.CreateNetworkInfo,
                                  original.CreateSubnetInfo,
                                  original.CreateSubnetDetail)
        else:
            try:
                CreateNetwork.unregister(original.CreateNetworkInfo)
                CreateNetwork.unregister(original.CreateSubnetInfo)
                CreateNetwork.unregister(original.CreateSubnetDetail)
            except base.NotRegistered:
                pass
            self.default_steps = (CreateNetworkInfo,
                                  CreateSubnetType,
                                  CreateSubnetInfo,
                                  CreateSubnetDetail)
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

    def _create_subnet(self, request, data, network=None,
                       no_redirect=False):
        if network:
            network_id = network.id
            network_name = network.name
        else:
            network_id = self.context.get('network_id')
            network_name = self.context.get('network_name')
        try:
            # TODO refactoring This code is duplicated from the subnet workflow
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
