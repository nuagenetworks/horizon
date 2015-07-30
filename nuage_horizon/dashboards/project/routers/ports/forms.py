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

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.dashboards.project.routers.ports \
    import forms as original

from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class SetGatewayForm(original.SetGatewayForm):
    snat = forms.ChoiceField(label=_("SNAT"),
                             choices=[("", _("Default")),
                                      ("enabled", _("Enabled")),
                                      ("disabled", _("Disabled"))],
                             required=False)

    def __init__(self, request, *args, **kwargs):
        super(SetGatewayForm, self).__init__(request, *args, **kwargs)
        if not request.user.is_superuser:
            del self.fields['snat']

    def handle(self, request, data):
        try:
            enable_snat = (data['snat'] == 'enabled'
                           if data.get('snat') else None)
            neutron.router_add_gateway(request,
                                       data['router_id'],
                                       data['network_id'],
                                       enable_snat)
            msg = _('Gateway interface is added')
            LOG.debug(msg)
            messages.success(request, msg)
            return True
        except Exception as e:
            msg = _('Failed to set gateway %s') % e
            LOG.info(msg)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
