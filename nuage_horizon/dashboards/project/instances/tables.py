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
import time

from nuage_horizon.api import neutron
from threading import Thread

from openstack_dashboard.dashboards.project.instances import tables as original
from openstack_dashboard import api


def func(neutron_ports, obj_id, request):
    try:
        server = api.nova.server_get(request, obj_id)
        count = 0
        while server.status != 'DELETED' and count < 6:
            server = api.nova.server_get(request, obj_id)
            time.sleep(5)
            count += 1
    except Exception:
        pass
    for port in neutron_ports:
        if port['device_owner'] == 'appd':
            neutron.appdport_delete(request, port.id)


def action(self, request, obj_id):
    neutron_ports = neutron.port_list(request, device_id=obj_id)
    api.nova.server_delete(request, obj_id)

    # Don't want to lock UI waiting on VM destroy.
    thread = Thread(target=func,
                    args=(neutron_ports, obj_id, request))
    thread.start()

original.TerminateInstance.action = action
