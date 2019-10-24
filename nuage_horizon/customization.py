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

from django.conf import settings

from nuage_horizon.dashboards.admin import networks  # noqa
from nuage_horizon.dashboards.admin.networks import subnets  # noqa
from nuage_horizon.dashboards.project import dashboard  # noqa
from nuage_horizon.dashboards.project import gateways  # noqa
from nuage_horizon.dashboards.project import network_topology  # noqa
from nuage_horizon.dashboards.project import networks  # noqa
from nuage_horizon.dashboards.project.networks import subnets  # noqa
from nuage_horizon.dashboards.project import routers  # noqa
from nuage_horizon.dashboards.project import security_groups  # noqa


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
# Add nuage_horizon/static to the Django static_dirs.
# Usage like <script src='{{ STATIC_URL }}nuage/js/NuageLinkedSelect.js' ...
settings.STATICFILES_DIRS.append(('nuage', os.path.join(ROOT_PATH, 'static'),))
settings.SITE_BRANDING = 'Nuage OpenStack'
