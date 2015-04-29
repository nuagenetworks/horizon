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
import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__)


class DeleteApplicationDomain(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Application Domain",
            u"Delete Applications Domains",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Application Domain",
            u"Deleted Application Domains",
            count
        )

    def delete(self, request, application_id):
        app = self.table.get_object_by_id(application_id)
        try:
            neutron.application_domain_delete(request, application_id)
            LOG.debug('Deleted application domain %s successfully', app.name)
        except Exception:
            msg = _('Failed to delete application domain %s' % application_id)
            LOG.info(msg)
            redirect = reverse("horizon:project:application_domains:index")
            usrmsg = _('Failed to delete application domain %s' % app.name)
            exceptions.handle(request, usrmsg, redirect=redirect)


class CreateApplicationDomain(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Application Domain")
    url = "horizon:project:application_domains:create"
    classes = ("ajax-modal",)
    icon = "plus"


class EditApplicationDomain(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Application Domain")
    url = "horizon:project:application_domains:update"
    classes = ("ajax-modal",)
    icon = "pencil"


class ApplicationDomainsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:application_domains:detail')
    description = tables.Column("description",
                                verbose_name=_("Description"))

    class Meta:
        name = "appdomains"
        verbose_name = _("Application Domains")
        table_actions = (CreateApplicationDomain, DeleteApplicationDomain)
        row_actions = (EditApplicationDomain, DeleteApplicationDomain)
