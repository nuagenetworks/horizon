# Copyright 2018 NOKIA
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
from django.core.urlresolvers import reverse

from nuage_horizon.dashboards.project.networks import\
    views as n_views
from nuage_horizon.dashboards.project.networks import\
    workflows as n_workflows


class NuageNTCreateNetwork(n_workflows.CreateNetwork):
    def get_success_url(self):
        return reverse("horizon:project:network_topology:index")

    def get_failure_url(self):
        return reverse("horizon:project:network_topology:index")


class NuageNTCreateNetworkView(n_views.NuageCreateView):
    workflow_class = NuageNTCreateNetwork
