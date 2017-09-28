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

from django.conf.urls import url
from openstack_dashboard.dashboards.admin.networks import urls as original

from nuage_horizon.dashboards.admin.networks import views
from nuage_horizon.dashboards.project.networks.subnets \
    import views as subnet_views


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'

for i, pattern in enumerate(original.urlpatterns):
    if getattr(pattern, 'name', '') == 'detail':
        original.urlpatterns[i] = url(NETWORKS % 'detail',
                                      views.NuageDetailView.as_view(),
                                      name='detail')
    elif getattr(pattern, 'name', '') == 'createsubnet':
        original.urlpatterns[i] = url(NETWORKS % 'subnets/create',
                                      subnet_views.CreateView.as_view(),
                                      name='createsubnet')
