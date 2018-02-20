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

from django.conf.urls import url
from openstack_dashboard.dashboards.project.security_groups \
    import urls as original

from nuage_horizon.dashboards.project.security_groups import views


for i, pattern in enumerate(original.urlpatterns):
    if getattr(pattern, 'name', '') == 'index':
        original.urlpatterns[i] = url(r'^$', views.NuageIndexView.as_view(),
                                      name='index')
    elif getattr(pattern, 'name', '') == 'create':
        original.urlpatterns[i] = url(r'^create$',
                                      views.NuageCreateView.as_view(),
                                      name='create')
    elif getattr(pattern, 'name', '') == 'update':
        original.urlpatterns[i] = url(r'^(?P<security_group_id>[^/]+)/update/$',
                                      views.NuageUpdateView.as_view(),
                                      name='update')
