# Copyright 2015 Alcatel-Lucent USA Inc.
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
from django.conf.urls import url
from openstack_dashboard.dashboards.project.networks import urls as original

from nuage_horizon.dashboards.project.networks import views
from nuage_horizon.dashboards.project.networks.subnets \
    import views as subnet_views


for i, pattern in enumerate(original.urlpatterns):
    if getattr(pattern, 'name', '') == 'create':
        original.urlpatterns[i] = url(r'^create$',
                                      views.NuageCreateView.as_view(),
                                      name='create')
    elif getattr(pattern, 'name', '') == 'createsubnet':
        original.urlpatterns[i] = url(original.NETWORKS % 'subnets/create',
                                      subnet_views.CreateView.as_view(),
                                      name='createsubnet')

original.urlpatterns.append(
    url(r'^listOrganizations', views.organization_data,
        name='listOrganizations'))
original.urlpatterns.append(
    url(r'^listDomains$', views.domain_data, name='listDomains'))
original.urlpatterns.append(
    url(r'^listZones', views.zone_data, name='listZones'))
original.urlpatterns.append(
    url(r'^listSubnets', views.subnet_data, name='listSubnets'))
