# Copyright 2017 NOKIA
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

from openstack_dashboard.dashboards.admin.networks import \
    workflows as original

from nuage_horizon.dashboards.project.networks import \
    workflows as project_workflows
from nuage_horizon.dashboards.admin.networks import forms


class NuageCreateNetwork(original.CreateNetwork):
    default_steps = (original.CreateNetworkInfo,
                     project_workflows.CreateSubnetType,
                     project_workflows.CreateSubnetInfo,
                     project_workflows.CreateSubnetDetail)

    def __init__(self, request=None, context_seed=None, entry_point=None,
                 *args, **kwargs):
        self.create_network_form = forms.CreateNetwork(
            request, *args, **kwargs)
        super(original.CreateNetwork, self).__init__(
            request=request,
            context_seed=context_seed,
            entry_point=entry_point,
            *args, **kwargs)
