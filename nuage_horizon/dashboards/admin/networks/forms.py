# Copyright 2012 NEC Corporation
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import messages
from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.networks import forms as original


LOG = logging.getLogger(__name__)


class CreateNetwork(original.CreateNetwork):

    def __init__(self, request, *args, **kwargs):
        super(CreateNetwork, self).__init__(request, *args, **kwargs)
        choices = self.fields['network_type'].choices
        choices = [('', _("Select a network type"))] + (choices or [])
        self.fields['network_type'].choices = choices
        self.fields['network_type'].required = False

    def handle(self, request, data):
        try:
            params = {'name': data['name'],
                      'tenant_id': data['tenant_id'],
                      'admin_state_up': (data['admin_state'] == 'True'),
                      'shared': data['shared'],
                      'router:external': data['external']}
            if api.neutron.is_port_profiles_supported():
                params['net_profile_id'] = data['net_profile_id']
            if (api.neutron.is_extension_supported(request, 'provider')
                    and data['network_type']):
                network_type = data['network_type']
                params['provider:network_type'] = network_type
                if network_type in ['flat', 'vlan']:
                    params['provider:physical_network'] = (
                        data['physical_network'])
                if network_type in ['vlan', 'gre', 'vxlan']:
                    params['provider:segmentation_id'] = (
                        data['segmentation_id'])
            network = api.neutron.network_create(request, **params)
            msg = _('Network %s was successfully created.') % data['name']
            LOG.debug(msg)
            messages.success(request, msg)
            return network
        except Exception:
            redirect = reverse('horizon:admin:networks:index')
            msg = _('Failed to create network %s') % data['name']
            exceptions.handle(request, msg, redirect=redirect)

    def clean(self):
        cleaned_data = super(CreateNetwork, self).clean()
        if not cleaned_data['network_type']:
            del self._errors['segmentation_id']
        return cleaned_data
