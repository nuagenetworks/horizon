# Copyright 2020 Nokia.
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

from openstack_dashboard.dashboards.project.routers import views as original

from nuage_horizon.dashboards.project.routers import forms

LOG = logging.getLogger(__name__)


class NuageUpdateView(original.UpdateView):
    form_class = forms.NuageRouterUpdateForm

    def get_initial(self):
        router = self._get_object()
        initial = {'router_id': router['id'],
                   'tenant_id': router['tenant_id'],
                   'name': router['name'],
                   'description': router['description'],
                   'rd': router['rd'],
                   'rt': router['rt'],
                   'tunnel_type': router.get('tunnel_type'),
                   'admin_state': router['admin_state_up'],
                   'enable_snat':
                       (router.get('external_gateway_info') or {}).get(
                           'enable_snat'),
                   'external_gateway_info':
                       router.get('external_gateway_info'),
                   'routes': router.get('routes'),
                   'aggregate_flows': router.get('nuage_aggregate_flows'),
                   'underlay': router.get('nuage_underlay'),
                   'net_partition': router.get('net_partition'),
                   'ecmp_count': router.get('ecmp_count'),
                   'backhaul_vnid': router.get('nuage_backhaul_vnid'),
                   'backhaul_rd': router.get('nuage_backhaul_rd'),
                   'backhaul_rt': router.get('nuage_backhaul_rt'),
                   }
        if hasattr(router, 'distributed'):
            initial['mode'] = ('distributed' if router.distributed
                               else 'centralized')
        if hasattr(router, 'ha'):
            initial['ha'] = router.ha
        return initial


original.CreateView.form_class = forms.NuageRouterCreateForm
