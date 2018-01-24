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


from django.utils.translation import ugettext_lazy as _
from horizon import forms
from openstack_dashboard.dashboards.admin.networks import forms as original


LOG = logging.getLogger(__name__)


class CreateNetwork(original.CreateNetwork):

    with_subnet = forms.BooleanField(label=_("Create Subnet"),
                                     widget=forms.CheckboxInput(attrs={
                                         'class': 'switchable',
                                         'data-slug': 'with_subnet',
                                         'data-hide-tab': 'create_network__'
                                                          'createsubnetinfo'
                                                          'action,'
                                                          'create_network__'
                                                          'createsubnetdetail'
                                                          'action,'
                                                          'create_network__'
                                                          'createsubnettype'
                                                          'action',
                                         'data-hide-on-checked': 'false'
                                     }),
                                     initial=True,
                                     required=False)
