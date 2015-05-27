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
from openstack_dashboard.dashboards.project.routers import urls
from nuage_horizon.dashboards.project.routers import views


ROUTER_URL = r'^(?P<router_id>[^/]+)/%s'


def should_keep(pattern):
    return pattern.name != 'update' if hasattr(pattern, 'name') else True

urls.urlpatterns = [pat for pat in urls.urlpatterns if should_keep(pat)]

urls.urlpatterns.append(url(ROUTER_URL % 'update',
                            views.NuageUpdateView.as_view(),
                            name='update'))