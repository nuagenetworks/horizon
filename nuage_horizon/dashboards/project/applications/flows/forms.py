import copy
import logging

from itertools import chain

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django import forms as django_forms
from django.forms import util as form_utils
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from horizon import exceptions
from horizon import forms
from horizon import messages

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class CustomWidget(django_forms.Widget):
    def __init__(self, attrs=None, choices=()):
        super(CustomWidget, self).__init__(attrs)
        self.choices = list(choices)

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<div class="nuage-multi-choice">',
                              form_utils.flatatt(final_attrs))]
        options = self.render_options(final_attrs['name'], [value])
        if options:
            output.append(options)
        output.append('</div>')
        return mark_safe('\n'.join(output))

    def render_option(self, selected, name, value, label):
        option_value = force_text(name)
        if option_value in selected:
            selected_html = mark_safe('selected="selected"')
            selected.remove(option_value)
        else:
            selected_html = ''
        return format_html('<div><input type="checkbox" id="{0}" name="{1}" '
                           'value="{2}" {3}/><div><label for="{4}">{5}</label>'
                           '</div></div>',
                           value, name, label, selected_html, value,
                           force_text(label))

    def render_options(self, name, selected):
        selected = set(force_text(v) for v in selected)
        output = []
        for value, label in chain(self.choices):
            output.append(self.render_option(selected, name, value, label))
        return '\n'.join(output)


class MultiCheckboxField(forms.Field):
    widget = CustomWidget

    def __init__(self, choices=(), required=True, widget=None, label=None,
                 initial=None, help_text='', *args, **kwargs):
        super(MultiCheckboxField, self).__init__(required=required, widget=widget,
                                     label=label, initial=initial,
                                     help_text=help_text, *args, **kwargs)
        self.choices = choices

    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def __deepcopy__(self, memo):
        result = super(MultiCheckboxField, self).__deepcopy__(memo)
        result._choices = copy.deepcopy(self._choices, memo)
        return result


class CreateForm(forms.SelfHandlingForm):
    from_tier = forms.ChoiceField(label=_("From tier"))
    dest_tier = forms.ChoiceField(label=_("To tier"))
    name = forms.CharField(max_length=255, label=_("Name"))
    services = MultiCheckboxField(label=_('Services'), required=False)
    failure_url = 'horizon:project:applications:detail'

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        app_id = kwargs['initial']['application_id']
        tiers = neutron.tier_list(request, app_id=app_id)
        tier_choices = [(tier.id, tier.name) for tier in tiers]
        self.fields['from_tier'].choices = tier_choices
        self.fields['dest_tier'].choices = tier_choices

        services = neutron.application_service_list(request)
        service_choices = [(service.id, service.name) for service in services]
        self.fields['services'].choices = service_choices

    def is_valid(self):
        valid = super(CreateForm, self).is_valid()
        if self.data.get('from_tier') == self.data.get('dest_tier'):
            self.errors['dest_tier'] = self.error_class(
                [_('Destination tier can not be equal to origin tier.')])
            valid = False
        return valid

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        cleaned_data['services'] = self.data.getlist('services')
        return cleaned_data

    def handle(self, request, data):
        try:
            params = {'name': self.data['name'],
                      'origin_tier': self.data['from_tier'],
                      'dest_tier': self.data['dest_tier']}
            if data['services']:
                params['nuage_services'] = ','.join(data['services'])

            flow = neutron.flow_create(request, **params)
            msg = _('Flow %s was successfully created.') % data['name']
            messages.success(request, msg)
            return flow
        except Exception:
            msg = _('Failed to create flow "%s".') % data['name']
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
            neutron.flow_update(request, self.initial['flow_id'], **params)
            msg = _('Application %s was successfully updated.') % data['name']
            messages.success(request, msg)
            return True
        except Exception:
            msg = _('Failed to update application "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False