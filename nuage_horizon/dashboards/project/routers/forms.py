import logging

from horizon import exceptions
from horizon import forms
from horizon import messages

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from openstack_dashboard.dashboards.project.routers \
    import forms as router_forms

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class NuageRouterCreateForm(router_forms.CreateForm):
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


class NuageRouterUpdateForm(router_forms.UpdateForm):
    rd = forms.RegexField(r'\d+:\d+', label=_("Route Distinguisher"),
                          required=False)
    rt = forms.RegexField(r'\d+:\d+', label=_("Route Target"),
                          required=False)
    tunnel_type = forms.ChoiceField(label=_("Tunneling Type"),
                                    required=False)

    def __init__(self, request, *args, **kwargs):
        super(NuageRouterUpdateForm, self).__init__(request, *args, **kwargs)
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
            params = {'admin_state_up': (data['admin_state'] == 'True'),
                      'name': data['name']}
            if self.dvr_allowed:
                params['distributed'] = (data['mode'] == 'distributed')
            if self.ha_allowed:
                params['ha'] = data['ha']
            if data['rd']:
                params['rd'] = data['rd']
            if data['rt']:
                params['rt'] = data['rt']
            if data['tunnel_type'] and data['tunnel_type'] != 'default':
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
