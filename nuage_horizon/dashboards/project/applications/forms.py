import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255, label=_("description"),
                                  required=False)
    domain_id = forms.ChoiceField(label=_("Domain"))

    failure_url = 'horizon:project:applications:index'

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        app_domain_id = self.initial.get('domain_id')
        if app_domain_id:
            self.fields['domain_id'] = forms.CharField(
                label=_("Domain"),
                widget=forms.TextInput(attrs={'readonly': 'readonly'}),)
        else:
            app_domains = neutron.application_domain_list(request)
            domain_choices = [(domain.id, domain.name) for domain in app_domains]
            self.fields['domain_id'].choices = domain_choices

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'applicationdomain_id': data['domain_id'],
                      'description': data['description']}
            application = neutron.application_create(request, **params)
            msg = _('Application %s was successfully created.') % data['name']
            messages.success(request, msg)
            return application
        except Exception as exc:
            msg = _('Failed to create application "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Application Name"))
    domain_id = forms.CharField(
        label=_("Domain"),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),)

    failure_url = 'horizon:project:applications:index'

    def handle(self, request, data):
        try:
            params = {'name': data['name']}
            neutron.application_update(
                request, self.initial['application_id'], **params)
            msg = _('Application %s was successfully updated.') % data['name']
            messages.success(request, msg)
            return True
        except Exception as exc:
            msg = _('Failed to update application "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False