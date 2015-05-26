from dashboards.admin.networks import subnets # noqa
from dashboards.project import applications # noqa
from dashboards.project import application_domains # noqa
from dashboards.project import application_services # noqa
from dashboards.project import dashboard # noqa
from dashboards.project import gateways # noqa
from dashboards.project import gateway_vlans # noqa
from dashboards.project import instances # noqa
from dashboards.project import networks # noqa
from dashboards.project.networks import subnets # noqa
from dashboards.project import routers # noqa

import os

from django.conf import settings

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
# Add nuage_horizon/templates to the Django template_dirs.
# Add it first in the list so nuage templates take priority over the others.
settings.TEMPLATE_DIRS = ((os.path.join(ROOT_PATH, 'templates'),)
                          + settings.TEMPLATE_DIRS)
# Add nuage_horizon/static to the Django static_dirs.
# Usage like <script src='{{ STATIC_URL }}nuage/js/NuageLinkedSelect.js' ...
settings.STATICFILES_DIRS.append(('nuage', os.path.join(ROOT_PATH, 'static'),))
settings.SITE_BRANDING = 'Nuage OpenStack'