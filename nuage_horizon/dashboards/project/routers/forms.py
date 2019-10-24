import logging

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.routers \
    import forms as original

LOG = logging.getLogger(__name__)


class NuageRouterCreateForm(original.CreateForm):
    rd = forms.RegexField(r'\d+:\d+', label=_("Route Distinguisher"),
                          required=False)
    rt = forms.RegexField(r'\d+:\d+', label=_("Route Target"),
                          required=False)
    tunnel_type = forms.ChoiceField(label=_("Tunneling Type"),
                                    required=False)

    def __init__(self, request, *args, **kwargs):
        super(NuageRouterCreateForm, self).__init__(request, *args, **kwargs)
        tunnel_type_choices = [('default', _('Default')),
                               ('VXLAN', _('VXLAN')),
                               ('GRE', _('GRE'))]
        self.fields['tunnel_type'].choices = tunnel_type_choices
        if not request.user.is_superuser:
            # admin-only fields
            del self.fields['rd']
            del self.fields['rt']
            del self.fields['tunnel_type']

    def handle(self, request, data):
        try:
            params = {'name': data['name']}
            if self.dvr_allowed and data['mode'] != 'server_default':
                params['distributed'] = (data['mode'] == 'distributed')
            if self.ha_allowed and data['ha'] != 'server_default':
                params['ha'] = (data['ha'] == 'enabled')

            if request.user.is_superuser:
                if data['rd']:
                    params['rd'] = data['rd']
                if data['rt']:
                    params['rt'] = data['rt']
                if data['tunnel_type'] and data['tunnel_type'] != 'default':
                    params['tunnel_type'] = data['tunnel_type']

            router = api.neutron.router_create(request, **params)
            message = _('Router %s was successfully created.') % data['name']
            messages.success(request, message)
            return router
        except Exception as exc:
            if exc.status_code == 409:
                msg = _('Quota exceeded for resource router.')
            else:
                msg = _('Failed to create router "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class NuageRouterUpdateForm(original.UpdateForm):
    rd = forms.RegexField(r'\d+:\d+', label=_("Route Distinguisher"),
                          required=False)
    rt = forms.RegexField(r'\d+:\d+', label=_("Route Target"),
                          required=False)
    tunnel_type = forms.ChoiceField(label=_("Tunneling Type"),
                                    required=False,
                                    choices=[('default', _('Default')),
                                             ('VXLAN', _('VXLAN')),
                                             ('GRE', _('GRE'))])
    snat_enabled = forms.BooleanField(label=_("SNAT enabled"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(NuageRouterUpdateForm, self).__init__(request, *args, **kwargs)
        if not request.user.is_superuser:
            # admin-only fields
            del self.fields['rd']
            del self.fields['rt']
            del self.fields['tunnel_type']
        if (not request.user.is_superuser or
                kwargs['initial']['snat_enabled'] is None):
            del self.fields['snat_enabled']

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
            if 'snat_enabled' in data:
                params['external_gateway_info'] = (
                    self.initial['external_gateway_info'])
                params['external_gateway_info']['enable_snat'] = (
                    data['snat_enabled'])
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
