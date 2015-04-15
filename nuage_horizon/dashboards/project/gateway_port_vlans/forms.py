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
    tenant_id = forms.ChoiceField(label=_("Tenant"),
                                  required=False)
    type = forms.ChoiceField(label=_("Type"),
                             choices=[('', _("Select a vport type")),
                                      ('host', _('Host')),
                                      ('bridge', _('Bridge'))],
                             required=False)
    subnet_id = UnsafeChoiceField(label=_("Subnet"),
                                  required=False)
    port_id = UnsafeChoiceField(label=_("Port"),
                                required=False)
    failure_url = 'horizon:project:gateways:ports:detail'

    def __init__(self, request, *args, **kwargs):
        super(VlanForm, self).__init__(request, *args, **kwargs)
        if kwargs.get('data'):
            data = kwargs['data']
        else:
            data = kwargs.get('initial')
        tenant_id = data.get('tenant_id')
        type = data.get('type')
        subnet_id = data.get('subnet_id')
        port_id = data.get('subnet_id')
        gw_port = kwargs['initial']['gw_port']

        result = vlan_regex.match(gw_port.get('vlan'))
        if result:
            self.fields['vlan'] = forms.IntegerField(
                label=_("VLAN"),
                min_value=int(result.groups()[0]),
                max_value=int(result.groups()[1]))

        if request.user.is_superuser:
            tenant_choices = [('', _("Select a tenant"))]
            tenants, has_more = api.keystone.tenant_list(request)
            for tenant in tenants:
                if tenant.enabled:
                    tenant_choices.append((tenant.id, tenant.name))
            self.fields['tenant_id'].choices = tenant_choices
        else:
            del self.fields['tenant_id']

        subnet_choices = [('', _("Select a subnet"))]
        if tenant_id and type:
            subnet_list = neutron.subnet_list(request, tenant_id=tenant_id)
            choices = [(subnet['id'], subnet['name'] + ' - ' + subnet['cidr'])
                       for subnet in subnet_list]
            subnet_choices.extend(choices)
        self.fields['subnet_id'].choices = subnet_choices

        port_choices = [('', _("Select a port"))]
        if tenant_id and type and type == 'host' and subnet_id:
            port_list = neutron.port_list(request,
                                          fixed_ips='subnet_id=' + subnet_id)

            choices = [(port['id'], port['fixed_ips'][0]['ip_address'])
                       for port in port_list
                       if ((not port['device_owner'] and not port['device_id'])
                           or port['id'] == port_id)]
            port_choices.extend(choices)

        self.fields['port_id'].choices = port_choices


class CreateForm(VlanForm):

    @staticmethod
    def create_gw_port_vlan(request, gw_port_id, vlan, tenant_id,
                            type, subnet_id, port_id):
        gw_port_vlan = neutron.nuage_gateway_port_vlan_create(
            request, gw_port_id=gw_port_id, vlan=vlan)
        if tenant_id:
            neutron.nuage_gateway_port_vlan_assign(
                request, gw_port_vlan['id'], tenant_id=tenant_id)
        if type == 'host':
            neutron.nuage_gateway_vport_create(
                request,
                gw_port_vlan_id=gw_port_vlan['id'],
                port_id=port_id,
                tenant_id=tenant_id)
        elif type == 'bridge':
            neutron.nuage_gateway_vport_create(
                request,
                gw_port_vlan_id=gw_port_vlan['id'],
                subnet_id=subnet_id,
                tenant_id=tenant_id)
        return gw_port_vlan

    def is_valid(self):
        valid = super(CreateForm, self).is_valid()
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

    def handle(self, request, data):
        gw_port_vlan = None
        gw_port_id = self.initial.get('gw_port_id')
        try:
            vlan = data['vlan']
            tenant_id = data['tenant_id']
            type = data['type']
            subnet_id = data['subnet_id']
            port_id = data['port_id']

            gw_port_vlan = self.create_gw_port_vlan(request, gw_port_id, vlan,
                                                    tenant_id, type, subnet_id,
                                                    port_id)

            message = _('Gateway Port Vlan with vlan %s was successfully '
                        'created.') % vlan
            messages.success(request, message)
            return gw_port_vlan
        except Exception:
            if gw_port_vlan:
                neutron.nuage_gateway_port_vlan_delete(request,
                                                       gw_port_vlan['id'])
            msg = _('Failed to create Gateway Port Vlan.')
            LOG.info(msg)
            args = [gw_port_id]
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False


class UpdateForm(VlanForm):
    def __init__(self, request, *args, **kwargs):
        data = kwargs.get('initial')
        if data.get('subnet_id'):
            self.tenant_id = forms.CharField(
                label=_("Tenant"),
                required=False,
                widget=forms.TextInput(
                    attrs={'readonly': 'readonly'}))
        super(UpdateForm, self).__init__(request, *args, **kwargs)
        self.fields['vlan'].widget=forms.TextInput(
            attrs={'readonly': 'readonly'})

    def delete_gw_port_vlan(self, gw_port_vlan_id, request):
        gw_port_vlan = neutron.nuage_gateway_port_vlan_get(self.request,
                                                           gw_port_vlan_id)
        try:
            vport = gw_port_vlan.get('vport')
            if vport:
                neutron.nuage_gateway_vport_delete(request, vport)
            neutron.nuage_gateway_port_vlan_delete(request, gw_port_vlan_id)
        except Exception:
            msg = _('Failed to delete Gateway Port Vlan %s')
            LOG.info(msg, gw_port_vlan_id)
            redirect = reverse("horizon:project:gateways:ports:detail",
                               args=[gw_port_vlan['gatewayport']])
            exceptions.handle(request, msg % gw_port_vlan_id, redirect=redirect)

    def handle(self, request, data):
        gw_port = self.initial['gw_port']
        gw_port_id = gw_port.get('id')

        try:
            gw_port_vlan_id = self.initial['gw_port_vlan_id']
            vlan = data['vlan']
            tenant_id = data.get('tenant_id', request.user.tenant_id)
            type = data.get('type')
            subnet_id = data.get('subnet_id')
            port_id = data.get('port_id')

            if request.user.is_superuser:
                # neutron.nuage_gateway_port_vlan_unassign(
                #     request,
                #     gw_port_vlan_id,
                #     tenant_id=self.initial['tenant_id'])
                if tenant_id and self.initial['tenant_id'] != tenant_id:
                    neutron.nuage_gateway_port_vlan_assign(
                        request, gw_port_vlan_id, tenant_id=tenant_id)

            if not self.initial['type']:
                if type == 'host' and subnet_id and port_id:
                    neutron.nuage_gateway_vport_create(
                        request,
                        gw_port_vlan_id=gw_port_vlan_id,
                        port_id=port_id,
                        tenant_id=tenant_id)
                elif type == 'bridge' and subnet_id:
                    neutron.nuage_gateway_vport_create(
                        request,
                        gw_port_vlan_id=gw_port_vlan_id,
                        subnet_id=subnet_id,
                        tenant_id=tenant_id)

            message = _('Gateway Port Vlan with vlan %s was successfully '
                        'updated.') % vlan
            messages.success(request, message)
            return True
        except Exception:
            msg = _('Failed to update Gateway Port Vlan.')
            LOG.info(msg)
            args = [gw_port_id]
            redirect = reverse(self.failure_url, args=args)
            exceptions.handle(request, msg, redirect=redirect)
            return False