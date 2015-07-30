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
from django.utils.translation import ungettext_lazy

from horizon import tables
from horizon import exceptions

from openstack_dashboard import policy
from openstack_dashboard.dashboards.project.networks.ports \
    import tables as original
from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


class AddAllowedAddressPair(policy.PolicyTargetMixin, tables.LinkAction):
    name = "AddAllowedAddressPair"
    verbose_name = _("Add allowed address pair")
    url = "horizon:project:networks:ports:addallowedaddresspairs"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("network", "update_port"),)

    def allowed(self, request, port):
        allowed = super(AddAllowedAddressPair, self).allowed(request, port)
        if not allowed:
            return allowed
        if not port:
            port_id = self.table.kwargs['port_id']
            port = neutron.port_get(request, port_id)
        subnet_id = port['fixed_ips'][0]['subnet_id']
        subnet = neutron.subnet_get(request, subnet_id, fields=['vsd_managed',
                                                                'ip_version'])
        return not subnet['vsd_managed']

    def get_link_url(self, port=None):
        if port:
            return reverse(self.url, args=(port.id,))
        else:
            return reverse(self.url, args=(self.table.kwargs.get('port_id'),))


class PortsTable(original.PortsTable):
    class Meta(object):
        name = "ports"
        verbose_name = _("Ports")
        row_actions = (original.UpdatePort, AddAllowedAddressPair)
        hidden_title = False


class DeleteAllowedAddressPair(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete",
            u"Delete",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted address pair",
            u"Deleted address pairs",
            count
        )

    policy_rules = (("network", "update_port"),)

    def delete(self, request, ip_address):
        try:
            port_id = self.table.kwargs['port_id']
            port = neutron.port_get(request, port_id)
            pairs = port.get('allowed_address_pairs', [])
            pairs = [pair for pair in pairs
                     if pair['ip_address'] != ip_address]
            neutron.port_update(request, port_id, allowed_address_pairs=pairs)
        except Exception:
            msg = _('Failed to update port %s')
            LOG.info(msg, port_id)
            redirect = reverse("horizon:project:networks:ports:detail",
                               args=(port_id,))
            exceptions.handle(request, msg % port_id, redirect=redirect)


class AllowedAddressPairsTable(tables.DataTable):
    IP = tables.Column("ip_address",
                       verbose_name=_("IP address"))
    mac = tables.Column('mac_address', verbose_name=_("MAC"))

    def get_object_display(self, address_pair):
        return address_pair['ip_address']

    class Meta(object):
        name = "allowedaddresspairs"
        verbose_name = _("Allowed address pairs")
        row_actions = (DeleteAllowedAddressPair,)
        table_actions = (AddAllowedAddressPair, DeleteAllowedAddressPair)
        hidden_title = False
