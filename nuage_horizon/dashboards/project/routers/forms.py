import logging

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.routers \
    import forms as original

from nuage_horizon.api import neutron as nuage_neutron

LOG = logging.getLogger(__name__)


class NuageRouterCreateForm(original.CreateForm):
    # Override enable_snat so it defaults to False
    enable_snat = forms.BooleanField(label=_("Enable SNAT (to overlay)"),
                                     initial=False,
                                     required=False)

    netpartition = forms.ChoiceField(label=_("Nuage netpartition"),
                                     required=False)
    router_template = forms.CharField(label=_("Nuage router template"),
                                      required=False)
    rd = forms.RegexField(r'\d+:\d+', label=_("Nuage Route Distinguisher"),
                          required=False)
    rt = forms.RegexField(r'\d+:\d+', label=_("Nuage Route Target"),
                          required=False)
    tunnel_type = forms.ChoiceField(label=_("Nuage Tunneling Type"),
                                    required=False)
    backhaul_rd = forms.RegexField(r'\d+:\d+',
                                   label=_("Nuage Backhaul Route "
                                           "Distinguisher"),
                                   required=False)
    backhaul_rt = forms.RegexField(r'\d+:\d+',
                                   label=_("Nuage Backhaul Route Target"),
                                   required=False)
    backhaul_vnid = forms.IntegerField(
        label=_("Nuage backhaul VNID"), required=False,
        help_text=_("Backhaul network's globally unique "
                    "VXLAN network identifier"))
    ecmp_count = forms.IntegerField(
        label=_("Nuage ECMP count"), required=False,
        min_value=1, max_value=8,
        help_text=_("Domain specific Equal-cost multi-path routing count, "
                    "ECMPCount = 1 means no ECMP"))
    underlay = forms.ChoiceField(label=_("Nuage Underlay routing"),
                                 required=False)
    aggregate_flows = forms.ChoiceField(label=_("Nuage aggregate flows"),
                                        required=False)

    def __init__(self, request, *args, **kwargs):
        super(NuageRouterCreateForm, self).__init__(request, *args, **kwargs)
        tunnel_type_choices = [('default', _('Default')),
                               ('VXLAN', _('VXLAN')),
                               ('GRE', _('GRE'))]
        self.fields['tunnel_type'].choices = tunnel_type_choices

        underlay_choices = [('default', _('Default')),
                            ('off', _('Off')),
                            ('route', _('Route to Underlay')),
                            ('snat', _('SNAT to underlay'))]
        self.fields['underlay'].choices = underlay_choices

        aggregate_flows_choices = [('default', _('Default')),
                                   ('off', _('Off')),
                                   ('route', _('Route based')),
                                   ('pbr', _('PBR based'))]
        self.fields['aggregate_flows'].choices = aggregate_flows_choices

        netpartitions = self.get_netpartitions_name_list(request)
        if netpartitions:
            self.fields['netpartition'].choices = netpartitions
        else:
            del self.fields['netpartition']

        if not request.user.is_superuser:
            # admin-only fields
            del self.fields['netpartition']
            del self.fields['router_template']
            del self.fields['rd']
            del self.fields['rt']
            del self.fields['tunnel_type']
            del self.fields['backhaul_rd']
            del self.fields['backhaul_rt']
            del self.fields['backhaul_vnid']
            del self.fields['ecmp_count']
            del self.fields['underlay']
            del self.fields['aggregate_flows']

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'admin_state_up': data['admin_state_up']}
            # NOTE: admin form allows to specify tenant_id.
            # We have the logic here to simplify the logic.
            if 'tenant_id' in data and data['tenant_id']:
                params['tenant_id'] = data['tenant_id']
            if 'external_network' in data and data['external_network']:
                params['external_gateway_info'] = {'network_id':
                                                   data['external_network']}
                if self.enable_snat_allowed:
                    params['external_gateway_info']['enable_snat'] = \
                        data['enable_snat']
            if 'az_hints' in data and data['az_hints']:
                params['availability_zone_hints'] = data['az_hints']
            if (self.dvr_allowed and data['mode'] != 'server_default'):
                params['distributed'] = (data['mode'] == 'distributed')
            if (self.ha_allowed and data['ha'] != 'server_default'):
                params['ha'] = (data['ha'] == 'enabled')

            # Nuage specific resources
            if request.user.is_superuser:
                if data.get('netpartition') and data['netpartition'] != 'default':
                    params['net_partition'] = data['netpartition']
                if data.get('router_template'):
                    params['nuage_router_template'] = data['router_template']
                if data.get('rd'):
                    params['rd'] = data['rd']
                if data.get('rt'):
                    params['rt'] = data['rt']
                if data.get('tunnel_type') and data['tunnel_type'] != 'default':
                    params['tunnel_type'] = data['tunnel_type']
                if data.get('backhaul_rd'):
                    params['backhaul_rd'] = data['backhaul_rd']
                if data.get('backhaul_rt'):
                    params['nuage_backhaul_rt'] = data['backhaul_rt']
                if data.get('backhaul_vnid'):
                    params['nuage_router_template'] = data['backhaul_vnid']
                if data.get('ecmp_count'):
                    params['ecmp_count'] = data['ecmp_count']
                if data.get('underlay') and data['underlay'] != 'default':
                    params['nuage_underlay'] = data['underlay']
                if (data.get('aggregate_flows') and
                        data['aggregate_flows'] != 'default'):
                    params['nuage_aggregate_flows'] = data['aggregate_flows']

            router = api.neutron.router_create(request, **params)
            message = (_('Router %s was successfully created.') %
                       router.name_or_id)
            messages.success(request, message)
            return router
        except Exception as exc:
            LOG.info('Failed to create router: %s', exc)
            if exc.status_code == 409:
                msg = _('Quota exceeded for resource router.')
            else:
                msg = _('Failed to create router "%s".') % data['name']
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False

    @staticmethod
    def get_netpartitions_name_list(request):
        netpartitions = nuage_neutron.nuage_netpartitions_list(request)

        netpartition_names = [(np['id'], np['name']) for np in netpartitions]
        return [('default', _('Default'))] + netpartition_names


class NuageRouterUpdateForm(original.UpdateForm):
    enable_snat = forms.BooleanField(label=_("Enable SNAT (to overlay)"),
                                     required=False)

    rd = forms.RegexField(r'\d+:\d+', label=_("Nuage Route Distinguisher"),
                          required=False)
    rt = forms.RegexField(r'\d+:\d+', label=_("Nuage Route Target"),
                          required=False)
    tunnel_type = forms.ChoiceField(label=_("Tunneling Type"),
                                    required=False,
                                    choices=[('default', _('Default')),
                                             ('VXLAN', _('VXLAN')),
                                             ('GRE', _('GRE'))])
    backhaul_rd = forms.RegexField(r'\d+:\d+',
                                   label=_("Nuage Backhaul Route "
                                           "Distinguisher"),
                                   required=False)
    backhaul_rt = forms.RegexField(r'\d+:\d+',
                                   label=_("Nuage Backhaul Route Target"),
                                   required=False)
    backhaul_vnid = forms.IntegerField(
        label=_("Nuage backhaul VNID"), required=False,
        help_text=_("Backhaul network's globally unique "
                    "VXLAN network identifier"))
    ecmp_count = forms.IntegerField(
        label=_("Nuage ECMP count"), required=False,
        min_value=1, max_value=8,
        help_text=_("Domain specific Equal-cost multi-path routing count, "
                    "ECMPCount = 1 means no ECMP"))
    underlay = forms.ChoiceField(label=_("Nuage Underlay routing"),
                                 required=False,
                                 choices=[('off', _('Off')),
                                          ('route', _('Route to Underlay')),
                                          ('snat', _('SNAT to underlay'))])
    aggregate_flows = forms.ChoiceField(label=_("Nuage aggregate flows"),
                                        required=False,
                                        choices=[('off', _('Off')),
                                                 ('route', _('Route based')),
                                                 ('pbr', _('PBR based'))])

    def __init__(self, request, *args, **kwargs):
        super(NuageRouterUpdateForm, self).__init__(request, *args, **kwargs)
        if not request.user.is_superuser:
            # admin-only fields
            del self.fields['rd']
            del self.fields['rt']
            del self.fields['tunnel_type']
            del self.fields['backhaul_rd']
            del self.fields['backhaul_rt']
            del self.fields['backhaul_vnid']
            del self.fields['ecmp_count']
            del self.fields['underlay']
            del self.fields['aggregate_flows']
        if (not request.user.is_superuser or
                kwargs['initial']['enable_snat'] is None):
            del self.fields['enable_snat']

    def handle(self, request, data):
        try:
            params = {'admin_state_up': (data['admin_state'] == 'True'),
                      'name': data['name']}
            if self.dvr_allowed:
                params['distributed'] = (data['mode'] == 'distributed')
            if self.ha_allowed:
                params['ha'] = data['ha']
            if 'rd' in data:
                params['rd'] = data['rd']
            if 'rt' in data:
                params['rt'] = data['rt']
            if 'enable_snat' in data:
                params['external_gateway_info'] = (
                    self.initial['external_gateway_info'])
                params['external_gateway_info']['enable_snat'] = (
                    data['enable_snat'])
            if 'tunnel_type' in data and data['tunnel_type'] != 'default':
                params['tunnel_type'] = data['tunnel_type']
            router = api.neutron.router_update(request, data['router_id'],
                                               **params)
            msg = _('Router %s was successfully updated.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return router
        except Exception:
            msg = _('Failed to update router %s') % data['name']
            LOG.info(msg)
            exceptions.handle(request, msg, redirect=self.redirect_url)
