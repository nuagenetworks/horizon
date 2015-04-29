from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.project import dashboard


class Applications(horizon.Panel):
    name = _("Applications")
    slug = 'applications'

dashboard.Project.register(Applications)
