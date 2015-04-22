from dashboards.project import routers
from dashboards.project import networks
from dashboards.project import gateways # noqa
from dashboards.project import gateway_vlans # noqa
from dashboards.project.networks import subnets
from dashboards.admin.networks import subnets
from dashboards.project import dashboard # noqa

import os

from horizon import loaders

root_dir = os.path.dirname(__file__)
static_dir = os.path.join(root_dir, "static")
loaders.panel_template_dirs['nuage/js'] = static_dir
