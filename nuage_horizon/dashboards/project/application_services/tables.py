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


class DeleteApplicationService(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Application Service",
            u"Delete Applications Services",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Application Service",
            u"Deleted Application Services",
            count
        )

    def delete(self, request, app_service_id):
        name = self.table.get_object_by_id(app_service_id).name
        try:
            neutron.application_service_delete(request, app_service_id)
            LOG.debug('Deleted application service %s successfully', name)
        except Exception as e:
            msg = _('Failed to delete application service %s. Details: %s'
                    % (app_service_id, e.message))
            LOG.info(msg)
            redirect = reverse("horizon:project:application_services:index")
            usrmsg = _('Failed to delete application service %s. Details: %s'
                       % (name, e.message))
            exceptions.handle(request, usrmsg, redirect=redirect)


class CreateApplicationService(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Application Service")
    url = "horizon:project:application_services:create"
    classes = ("ajax-modal",)
    icon = "plus"


class EditApplicationService(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Application Service")
    url = "horizon:project:application_services:update"
    classes = ("ajax-modal",)
    icon = "pencil"


class ApplicationServicesTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:application_services:detail')
    description = tables.Column("direction", verbose_name=_("Direction"))
    src_port = tables.Column("src_port", verbose_name=_("Source Port"))
    dest_port = tables.Column("dest_port", verbose_name=_("Destination Port"))
    dscp = tables.Column("dscp", verbose_name=_("dscp"))
    protocol = tables.Column("protocol", verbose_name=_("Protocol"))

    class Meta:
        name = "appservices"
        verbose_name = _("Application Services")
        table_actions = (CreateApplicationService, DeleteApplicationService)
        row_actions = (EditApplicationService, DeleteApplicationService)
