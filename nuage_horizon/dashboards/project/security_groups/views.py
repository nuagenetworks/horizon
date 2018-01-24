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

import json

from django import form
from openstack_dashboard.dashboards.project.security_groups \
    import views as original

from nuage_horizon.dashboards.project.security_groups \
    import forms
from nuage_horizon.dashboards.project.security_groups \
    import tables


class NuageCreateView(original.CreateView):
    form_class = forms.CreateNuageGroup


class NuageUpdateView(original.UpdateView):
    form_class = forms.UpdateNuageGroup

    def get_initial(self):
        security_group = self.get_object()
        return {'id': self.kwargs['security_group_id'],
                'name': security_group.name,
                'description': security_group.description,
                'stateful': security_group.stateful}


class NuageIndexView(original.IndexView):
    table_class = tables.NuageSecurityGroupsTable
