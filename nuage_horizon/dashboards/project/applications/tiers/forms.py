import logging

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class CreateForm(forms.SelfHandlingForm):
    type = forms.ChoiceField(
        label=_("Type"),
        choices=[('', 'Choose a tier type'),
                 ('STANDARD', 'Application Tier'),
                 ('NETWORK_MACRO', 'Network Macro'),
                 ('APPLICATION', 'Current Application'),
                 ('APPLICATION_EXTENDED_NETWORK', "Application's Domain")])
    name = forms.CharField(max_length=255,
                           label=_("Name *"),
                           required=False)
    description = forms.CharField(max_length=255,
                                  label=_("Description"),
                                  required=False)
    cidr = forms.IPField(label=_("Address *"),
                         help_text=_("Tier's network address in CIDR format "
                                     "(e.g. 192.168.0.0/24, 2001:DB8::/48)"),
                         version=forms.IPv4 | forms.IPv6,
                         mask=True,
                         required=False)
    fip_pool = forms.ChoiceField(label=_("Fip pool"), required=False)
    failure_url = 'horizon:project:applications:detail'

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        fip_pools = neutron.network_list(request, **{'router:external': True})
        fip_choices = [('', _('Choose a fip subnet'))]
        for fip_net in fip_pools:
            fip_choices.extend(
                [(fip_subnet.id, fip_subnet.name)
                 for fip_subnet in fip_net.get('subnets')])
        self.fields['fip_pool'].choices = fip_choices

    def is_valid(self):
        valid = super(CreateForm, self).is_valid()
        required_by_type = {
            '': ['type'],
            'STANDARD': ['name', 'cidr'],
            'NETWORK_MACRO': ['name', 'cidr'],
            'APPLICATION': ['name'],
            'APPLICATION_EXTENDED_NETWORK': ['name']
        }
        required = required_by_type[self.data.get('type', '')]
        for field in required:
            if not self.data[field]:
                self.errors[field] = self.error_class(
                    [_('This is a required field.')])
                valid = False

        return valid

    def handle(self, request, data):
        try:
            params = {'app_id': self.initial.get('application_id'),
                      'type': self.data['type']}
            if data['name']:
                params['name'] = data['name']
            if data['description']:
                params['description'] = data['description']
            if data['cidr']:
                params['cidr'] = data['cidr']
            if data['fip_pool']:
                params['fip_pool_id'] = data['fip_pool']

            tier = neutron.tier_create(request, **params)
            msg = _('Tier %s was successfully created.') % data['name']
            messages.success(request, msg)
            return tier
        except Exception:
            msg = _('Failed to create tier "%s".') % data['name']
            LOG.info(msg)
            args = (self.initial.get('application_id'),)
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255,
                                  label=_("Description"),
                                  required=False)
    failure_url = reverse_lazy('horizon:project:applications:index')

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'description': data['description']}
            neutron.tier_update(request, self.initial['tier_id'], **params)
            msg = _('Application Tier %s was successfully updated.'
                    '') % data['name']
            messages.success(request, msg)
            return True
        except Exception:
            msg = _('Failed to update application tier "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False