# Copyright 2015 Alcatel-Lucent USA Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import messages
from horizon import exceptions

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255,
                                  label=_("Description"),
                                  required=False)
    failure_url = 'horizon:project:application_domains:index'

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'description': data['description']}
            app_domain = neutron.application_domain_create(request, **params)
            message = _('Application Domain %s was successfully created.'
                        '') % data['name']
            messages.success(request, message)
            return app_domain
        except Exception:
            msg = _('Failed to create Application Domain "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255,
                                  label=_("Description"),
                                  required=False)
    failure_url = 'horizon:project:application_domains:index'

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'description': data['description']}
            neutron.application_domain_update(
                request, self.initial['app_domain_id'], **params)
            message = _('Application Domain %s was successfully updated.'
                        '') % data['name']
            messages.success(request, message)
            return True
        except Exception:
            msg = _('Failed to update Application Domain "%s".') % data['name']
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False