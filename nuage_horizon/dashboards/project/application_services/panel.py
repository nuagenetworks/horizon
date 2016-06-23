from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.project import dashboard


class ApplicationServices(horizon.Panel):
    name = _("Application Services")
    slug = 'application_services'

dashboard.Project.register(ApplicationServices)
