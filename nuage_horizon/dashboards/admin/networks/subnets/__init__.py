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

from nuage_horizon.dashboards.admin.networks.subnets import views
from openstack_dashboard.dashboards.admin.networks import urls


def should_keep(pattern, name):
    return pattern.name != name if hasattr(pattern, 'name') else True


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'addsubnet')]
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'editsubnet')]

urls.urlpatterns.append(
    url(NETWORKS % 'subnets/create', views.CreateView.as_view(),
        name='addsubnet')
)
urls.urlpatterns.append(
    url(r'^(?P<network_id>[^/]+)/subnets/(?P<subnet_id>[^/]+)/update$',
        views.UpdateView.as_view(), name='editsubnet')
)
