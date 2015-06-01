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
import os


from horizon import loaders
from nuage_horizon.dashboards.project.networks import views
from . import urls  # noqa

network_dir = os.path.dirname(__file__)
template_dir = os.path.join(network_dir, "templates")
loaders.panel_template_dirs['nuage/networks'] = template_dir
