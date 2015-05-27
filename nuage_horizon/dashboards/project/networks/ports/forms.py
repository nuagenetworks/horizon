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
from horizon import forms
from horizon import messages

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class AddAllowedAddressPairForm(forms.SelfHandlingForm):
    ip = forms.IPField(label=_("Ip address"),
                         help_text=_("Virtual IP address"),
                         version=forms.IPv4 | forms.IPv6,
                         mask=False)
    mac = forms.CharField(max_length=17,
                          label=_("Mac"),
                          required=False,)
    failure_url = 'horizon:project:networks:ports:detail'

    def is_valid(self):
        valid = super(AddAllowedAddressPairForm, self).is_valid()
        mac = self.data['mac']
        if not mac:
            print 'should fail on invalid mac'

        return valid

    def handle(self, request, data):
        port_id = self.initial['port_id']
        try:
            port = neutron.port_get(request, port_id)

            current = port['allowed_address_pairs']
            pair = {'ip_address': data['ip']}
            if data['mac']:
                pair['mac_address'] = data['mac']
            current.append(pair)
            port = neutron.port_update(request, port_id,
                                       allowed_address_pairs=current)
            msg = _('Port %s was successfully updated.') % port_id
            messages.success(request, msg)
            return port
        except Exception as e:
            msg = _('Failed to update port "%s".') % port_id
            LOG.info(msg)
            args = (self.initial.get('port_id'),)
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False