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
import json
from django import http
from nuage_horizon.api import neutron
from openstack_dashboard.dashboards.project.instances import views as original


def tierData(request):
    app_id = request.GET.get('app_id')
    tier_list = neutron.tier_list(request, app_id=app_id)
    tier_list = [tier.to_dict() for tier in tier_list]
    response = http.HttpResponse(json.dumps(tier_list, ensure_ascii=False))
    return response


original.IndexView.template_name = 'nuage/instances/index.html'
