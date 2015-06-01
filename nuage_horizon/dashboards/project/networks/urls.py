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
from openstack_dashboard.dashboards.project.networks import urls
from nuage_horizon.dashboards.project.networks import views


def should_keep(pattern, name):
    return pattern.name != name if hasattr(pattern, 'name') else True


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'create')]
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'detail')]

urls.urlpatterns.append(
    url(r'^create$', views.NuageCreateView.as_view(), name='create'))
urls.urlpatterns.append(
    url(r'^listOrganizations', views.organization_data,
        name='listOrganizations'))
urls.urlpatterns.append(
    url(r'^listDomains$', views.domain_data, name='listDomains'))
urls.urlpatterns.append(
    url(r'^listZones', views.zone_data, name='listZones'))
urls.urlpatterns.append(
    url(r'^listSubnets', views.subnet_data, name='listSubnets'))
urls.urlpatterns.append(
    url(NETWORKS % 'detail', views.NuageDetailView.as_view(), name='detail'))
