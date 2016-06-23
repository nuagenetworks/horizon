from django.utils.translation import ugettext_lazy as _

import horizon

from openstack_dashboard.dashboards.project import dashboard


class ApplicationDomains(horizon.Panel):
    name = _("Application Domains")
    slug = 'application_domains'

dashboard.Project.register(ApplicationDomains)
