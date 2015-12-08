# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the 'License'); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.utils.text import normalize_newlines
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_variables

from horizon import exceptions
from horizon import forms
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances.workflows \
    import create_instance as original
from nuage_horizon.api import neutron

LOG = logging.getLogger(__name__)


def validate_net_tier_combo(action, actionclass):
    valid = super(actionclass, action).is_valid()
    if action.data.get('tier_id') and action.data.get('network'):
        error = action.error_class([_('Can not select both tier and network')])
        action._errors['__all__'] = error
        valid = False
    if not action.data.get('tier_id') and not action.data.get('network'):
        error = action.error_class(
            [_('Need to select either tier or network')])
        action._errors['__all__'] = error
        valid = False
    return valid


class UnsafeMultipleChoiceField(forms.MultipleChoiceField):
    """
    This is an extension of the default MultipleChoiceField with the exception
    that it will not validate that the value in the POST request matches the
    value during rendering of the Choicefield (In case Javascript alters the
    values client-side)
    """
    def valid_value(self, value):
        return True


class SetTierAction(workflows.Action):
    application_id = forms.ChoiceField(label=_('Application'),
                                       required=False)
    tier_id = UnsafeMultipleChoiceField(label=_('Tiers'),
                                        widget=forms.CheckboxSelectMultiple(),
                                        help_text=_('Launch instance with'
                                                    ' these tiers'),
                                        required=False)
    hidden_tiers = forms.CharField(widget=forms.HiddenInput,
                                   required=False)

    def __init__(self, request, *args, **kwargs):
        super(SetTierAction, self).__init__(request, *args, **kwargs)
        applications = neutron.application_list(request)
        app_choices = [('', _('Select an application'))]
        app_choices.extend([(app.id, app.name) for app in applications])
        self.fields['application_id'].choices = app_choices

    def is_valid(self):
        return validate_net_tier_combo(self, SetTierAction)

    class Meta(object):
        name = _('Application')
        help_text = _('First chose an Application. Then select tiers for your '
                      'instance.')


class SetTier(workflows.Step):
    action_class = SetTierAction
    template_name = 'nuage/instances/_update_tiers.html'
    contributes = ('tier_id',)

    def contribute(self, data, context):
        if data:
            tiers = self.workflow.request.POST.getlist('tier_id')
            if tiers:
                context['tier_id'] = tiers
        return context


def get_nics_from_networks(context, request, self):
    netids = context.get('network_id', None)
    if netids:
        nics = [{'net-id': netid, 'v4-fixed-ip': ''}
                for netid in netids]
    else:
        nics = None
    if api.neutron.is_port_profiles_supported():
        nics = self.set_network_port_profiles(request,
                                              context['network_id'],
                                              context['profile_id'])
    return nics


def boot_instance(request, avail_zone, context, custom_script, dev_mapping_1,
                  dev_mapping_2, image_id, nics, count):
    api.nova.server_create(request,
                           context['name'],
                           image_id,
                           context['flavor'],
                           context['keypair_id'],
                           normalize_newlines(custom_script),
                           context['security_group_ids'],
                           block_device_mapping=dev_mapping_1,
                           block_device_mapping_v2=dev_mapping_2,
                           nics=nics,
                           availability_zone=avail_zone,
                           instance_count=count,
                           admin_pass=context['admin_pass'],
                           disk_config=context.get('disk_config'),
                           config_drive=context.get('config_drive'))


def create_appdports(appdports, nics, request, tiers):
    for tier_id in tiers:
        appdport = neutron.appdport_create(
            request,
            tenant_id=request.user.tenant_id,
            tier_id=tier_id)
        appdports.append(appdport)
        nics.append({"port-id": appdport.id})


@sensitive_variables('context')
def handle(self, request, context):
    custom_script = context.get('script_data', '')

    dev_mapping_1 = None
    dev_mapping_2 = None

    image_id = ''

    # Determine volume mapping options
    source_type = context.get('source_type', None)
    if source_type in ['image_id', 'instance_snapshot_id']:
        image_id = context['source_id']
    elif source_type in ['volume_id', 'volume_snapshot_id']:
        dev_mapping_1 = {context['device_name']:
                         '%s::%s' %
                         (context['source_id'],
                          int(bool(context['delete_on_terminate'])))}
    elif source_type == 'volume_image_id':
        device_name = context.get('device_name', '').strip() or None
        dev_mapping_2 = [
            {'device_name': device_name,  # None auto-selects device
             'source_type': 'image',
             'destination_type': 'volume',
             'delete_on_termination': int(
                 bool(context['delete_on_terminate'])),
             'uuid': context['source_id'],
             'boot_index': '0',
             'volume_size': context['volume_size']
             }
        ]

    avail_zone = context.get('availability_zone', None)
    instance_count = int(context['count'])

    if context.get('network_id'):
        nics = get_nics_from_networks(context, request, self)
        boot_instance(request, avail_zone, context, custom_script,
                      dev_mapping_1, dev_mapping_2, image_id, nics,
                      instance_count)
    else:
        tiers = context.get('tier_id')
        base_name = context['name']
        for i in range(instance_count):
            if instance_count > 1:
                context['name'] = base_name + '-' + str(i+1)
            nics = []
            appdports = []
            try:
                create_appdports(appdports, nics, request, tiers)
                boot_instance(request, avail_zone, context, custom_script,
                              dev_mapping_1, dev_mapping_2, image_id, nics, 1)
            except Exception:
                for appdport in appdports:
                    neutron.appdport_delete(request, appdport.id)
                exceptions.handle(request)
                return False
        context['name'] = base_name

    return True


def set_network_port_profiles(self, request, net_ids, profile_id):
    # Create port with Network ID and Port Profile
    # for the use with the plugin supporting port profiles.
    nics = []
    for net_id in net_ids:
        try:
            port = api.neutron.port_create(
                request,
                net_id,
                policy_profile_id=profile_id,
            )
        except Exception as e:
            msg = (_('Unable to create port for profile '
                     '"%(profile_id)s": %(reason)s'),
                   {'profile_id': profile_id,
                    'reason': e})
            for nic in nics:
                try:
                    port_id = nic['port-id']
                    api.neutron.port_delete(request, port_id)
                except Exception:
                    msg = (msg +
                           _(' Also failed to delete port %s') % port_id)
            redirect = self.success_url
            exceptions.handle(request, msg, redirect=redirect)

        if port:
            nics.append({'port-id': port.id})
            LOG.debug('Created Port %(portid)s with '
                      'network %(netid)s '
                      'policy profile %(profile_id)s',
                      {'portid': port.id,
                       'netid': net_id,
                       'profile_id': profile_id})

    return nics


class SetNetworkAction(original.SetNetworkAction):
    def __init__(self, request, context, *args, **kwargs):
        super(SetNetworkAction, self).__init__(
            request, context, *args, **kwargs)
        self.fields['network'].required = False

    def is_valid(self):
        return validate_net_tier_combo(self, SetNetworkAction)

    class Meta(object):
        name = _("Networking")
        permissions = ('openstack.services.network',)
        help_text = _("Select networks for your instance.")

original.SetNetwork.action_class = SetNetworkAction
original.SetNetwork.template_name = 'nuage/instances/_update_networks.html'
original.LaunchInstance.default_steps = (original.SelectProjectUser,
                                         original.SetInstanceDetails,
                                         original.SetAccessControls,
                                         original.SetNetwork,
                                         SetTier,
                                         original.PostCreationStep,
                                         original.SetAdvanced)
original.LaunchInstance.handle = handle
