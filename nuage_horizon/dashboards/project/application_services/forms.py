import logging

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


def validate_port(port):
    if port == '*':
        return True
    try:
        port = int(port)
        return 0 < port < 65535
    except ValueError:
        raise ValidationError(_("Not a valid port number"))


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(label=_("Description"),
                                  required=False)
    protocol = forms.ChoiceField(label=_("Protocol"),
                                 choices=[('tcp', _('tcp')),
                                          ('udp', _('udp')),
                                          ('icmp', _('icmp'))])
    ethertype = forms.ChoiceField(label=_("Ether type"),
                                  choices=[('ipv4', _('ipv4')),
                                           ('ipv6', _('ipv6')),
                                           ('arp', _('arp'))])
    direction = forms.ChoiceField(
        label=_("Direction"),
        choices=[('REFLEXIVE', _('Reflexive')),
                 ('UNIDIRECTIONAL', _('Unidirectional')),
                 ('BIDIRECTIONAL', _('Bidirectional'))])
    dscp = forms.ChoiceField(label=_("DSCP"))
    src_port = forms.CharField(max_length=255,
                               label=_("Source port"),
                               initial='*',
                               validators=[validate_port])
    dest_port = forms.CharField(max_length=255,
                                label=_("Destination port"),
                                initial='*',
                                validators=[validate_port])
    failure_url = 'horizon:project:application_services:index'

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        dscp_choices = [('*', _('Any'))]
        for i in range(64):
            dscp_choices.append((i, i))
        self.fields['dscp'].choices = dscp_choices

    def handle(self, request, data):
        try:
            params = {'name': self.data['name'],
                      'protocol': self.data['protocol'],
                      'ethertype': self.data['ethertype'],
                      'direction': self.data['direction'],
                      }
            if data['description']:
                params['description'] = data['description']
            if data['dscp']:
                params['dscp'] = data['dscp']
            if data['src_port']:
                params['src_port'] = data['src_port']
            if data['dest_port']:
                params['dest_port'] = data['dest_port']

            neutron.application_service_create(request, **params)
            msg = _('Application Service %s was successfully created.'
                    '') % data['name']
            messages.success(request, msg)
            return True
        except Exception as e:
            msg = (_('Failed to create Application Service "%s".')
                   % data['name'])
            LOG.info(msg + '. Message: ' + e.message)
            error = self.error_class([_('Failed to create service.')])
            self._errors['__all__'] = error
            return False


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255,
                                  label=_("Description"),
                                  required=False)
    failure_url = reverse_lazy('horizon:project:application_services:index')

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'description': data['description']}
            neutron.application_service_update(
                request, self.initial['application_service_id'], **params)
            msg = _('Application Service %s was successfully updated.'
                    '') % data['name']
            messages.success(request, msg)
            return True
        except Exception:
            msg = (_('Failed to update application service "%s".')
                   % data['name'])
            LOG.info(msg)
            exceptions.handle(request, msg, redirect=self.failure_url)
            return False
