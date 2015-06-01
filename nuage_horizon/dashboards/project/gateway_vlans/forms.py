import logging
import re

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard import api

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__)
vlan_regex = re.compile(r'(\d+)-(\d+)')


class UnsafeChoiceField(forms.ChoiceField):
    """
    This is an extension of the default choicefield with the exception that it
    will not validate that the value in the POST request matches the value
    during rendering of the Choicefield (In case Javascript alters the values
    client-side)
    """
    def valid_value(self, value):
        return True


class VlanForm(forms.SelfHandlingForm):
    vlan = forms.IntegerField(label=_("VLAN"))
    assigned = forms.ChoiceField(label=_("Tenant"),
                                 required=False)
    type = forms.ChoiceField(label=_("Type"),
                             choices=[('', _("Select a vport type")),
                                      ('host', _('Host')),
                                      ('bridge', _('Bridge'))],
                             required=False)
    subnet_id = UnsafeChoiceField(label=_("Subnet"),
                                  required=False,
                                  choices=[('', _('Select a subnet'))])
    port_id = UnsafeChoiceField(label=_("Port"),
                                required=False,
                                choices=[('', _('Select a port'))])
    failure_url = 'horizon:project:gateways:ports:detail'

    def __init__(self, request, *args, **kwargs):
        super(VlanForm, self).__init__(request, *args, **kwargs)
        if kwargs.get('data'):
            data = kwargs['data']
        else:
            data = kwargs.get('initial')
        assigned = data.get('assigned')
        gw_port = kwargs['initial']['gw_port']

        if assigned:
            self.fields['assigned'] = forms.CharField(
                label=_("Tenant"),
                required=False,
                widget=forms.TextInput(
                    attrs={'readonly': 'readonly'}))
        elif request.user.is_superuser:
            tenant_choices = [('', _("Select a tenant"))]
            tenants, has_more = api.keystone.tenant_list(request)
            for tenant in tenants:
                if tenant.enabled:
                    tenant_choices.append((tenant.id, tenant.name))
            self.fields['assigned'].choices = tenant_choices
        else:
            del self.fields['assigned']

        result = vlan_regex.match(gw_port.get('vlan'))
        if result:
            self.fields['vlan'] = forms.IntegerField(
                label=_("VLAN"),
                min_value=int(result.groups()[0]),
                max_value=int(result.groups()[1]))

    def is_valid(self):
        valid = super(VlanForm, self).is_valid()
        if self.data['type'] == 'host':
            if not self.data['subnet_id']:
                self._errors['subnet_id'] = self.error_class(
                    ['This is a required field.'])
                valid = False
            if not self.data['port_id']:
                self._errors['port_id'] = self.error_class(
                    ['This is a required field.'])
                valid = False
        if self.data['type'] == 'bridge':
            if not self.data['subnet_id']:
                self._errors['subnet_id'] = self.error_class(
                    ['This is a required field.'])
                valid = False
        return valid


class CreateForm(VlanForm):

    @staticmethod
    def create_gw_vlan(request, gw_port_id, vlan, assigned, type, subnet_id,
                       port_id):
        gw_vlan = neutron.nuage_gateway_vlan_create(
            request, gw_port_id=gw_port_id, vlan=vlan)
        if assigned:
            neutron.nuage_gateway_vlan_assign(
                request, gw_vlan['id'], tenant_id=assigned)
        if type == 'host':
            neutron.nuage_gateway_vport_create(
                request,
                gw_vlan_id=gw_vlan['id'],
                port_id=port_id,
                tenant_id=assigned)
        elif type == 'bridge':
            neutron.nuage_gateway_vport_create(
                request,
                gw_vlan_id=gw_vlan['id'],
                subnet_id=subnet_id,
                tenant_id=assigned)
        return gw_vlan

    def handle(self, request, data):
        gw_vlan = None
        gw_port_id = self.initial.get('gw_port_id')
        try:
            vlan = data['vlan']
            assigned = data['assigned']
            type = data['type']
            subnet_id = data['subnet_id']
            port_id = data['port_id']

            gw_vlan = self.create_gw_vlan(request, gw_port_id, vlan,
                                          assigned, type, subnet_id,
                                          port_id)

            message = _('Gateway Vlan with vlan %s was successfully '
                        'created.') % vlan
            messages.success(request, message)
            return gw_vlan
        except Exception:
            if gw_vlan:
                neutron.nuage_gateway_vlan_delete(request, gw_vlan['id'])
            msg = _('Failed to create Gateway Vlan.')
            LOG.info(msg)
            args = [gw_port_id]
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class UpdateForm(VlanForm):
    def __init__(self, request, *args, **kwargs):
        super(UpdateForm, self).__init__(request, *args, **kwargs)
        self.fields['vlan'].widget = forms.TextInput(
            attrs={'readonly': 'readonly'})

    def delete_gw_vlan(self, gw_vlan_id, request):
        gw_vlan = neutron.nuage_gateway_vlan_get(self.request, gw_vlan_id)
        try:
            vport = gw_vlan.get('vport')
            if vport:
                neutron.nuage_gateway_vport_delete(request, vport)
            neutron.nuage_gateway_vlan_delete(request, gw_vlan_id)
        except Exception:
            msg = _('Failed to delete Gateway Vlan %s')
            LOG.info(msg, gw_vlan_id)
            redirect = reverse("horizon:project:gateways:ports:detail",
                               args=[gw_vlan['gatewayport']])
            exceptions.handle(request, msg % gw_vlan_id, redirect=redirect)

    def handle(self, request, data):
        gw_port = self.initial['gw_port']
        gw_port_id = gw_port.get('id')

        try:
            gw_vlan_id = self.initial['gw_vlan_id']
            vlan = data['vlan']
            assigned = data.get('assigned')
            type = data.get('type')
            subnet_id = data.get('subnet_id')
            port_id = data.get('port_id')

            if request.user.is_superuser:
                # neutron.nuage_gateway_vlan_unassign(
                #     request,
                #     gw_vlan_id,
                #     tenant_id=self.initial['tenant_id'])
                if assigned and self.initial['assigned'] != assigned:
                    neutron.nuage_gateway_vlan_assign(
                        request, gw_vlan_id, tenant_id=assigned)

            if not self.initial['type']:
                if type == 'host' and subnet_id and port_id:
                    neutron.nuage_gateway_vport_create(
                        request,
                        gw_vlan_id=gw_vlan_id,
                        port_id=port_id,
                        tenant_id=assigned)
                elif type == 'bridge' and subnet_id:
                    neutron.nuage_gateway_vport_create(
                        request,
                        gw_vlan_id=gw_vlan_id,
                        subnet_id=subnet_id,
                        tenant_id=assigned)

            message = _('Gateway Vlan with vlan %s was successfully '
                        'updated.') % vlan
            messages.success(request, message)
            return True
        except Exception:
            msg = _('Failed to update Gateway Vlan.')
            LOG.info(msg)
            args = [gw_port_id]
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False
