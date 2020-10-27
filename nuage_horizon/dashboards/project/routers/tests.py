# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
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

from django import http
from django.urls import reverse

from mox import IsA  # noqa

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.routers \
    import tests as router_tests
from openstack_dashboard.test import helpers as test
from openstack_dashboard.usage import quotas


class RouterTests(router_tests.RouterTests):
    DASHBOARD = 'project'
    INDEX_URL = reverse('horizon:%s:routers:index' % DASHBOARD)
    DETAIL_PATH = 'horizon:%s:routers:detail' % DASHBOARD

    @test.create_stubs({api.neutron: ('router_list', 'network_list'),
                        quotas: ('tenant_quota_usages',)})
    def test_index(self):
        quota_data = self.quota_usages.first()
        quota_data['routers']['available'] = 5
        api.neutron.router_list(
            IsA(http.HttpRequest),
            tenant_id=self.tenant.id,
            search_opts=None).AndReturn(self.routers.list())
        quotas.tenant_quota_usages(
            IsA(http.HttpRequest)) \
            .MultipleTimes().AndReturn(quota_data)
        self._mock_external_network_list()
        self.mox.ReplayAll()

        res = self.client.get(self.INDEX_URL)

        self.assertTemplateUsed(res, '%s/routers/index.html' % self.DASHBOARD)
        routers = res.context['table'].data
        self.assertItemsEqual(routers, self.routers.list())
