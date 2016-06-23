import logging

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy

from horizon import exceptions
from horizon import tables

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__)


class DeleteApplication(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Application",
            u"Delete Applications",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Application",
            u"Deleted Applications",
            count
        )

    def delete(self, request, application_id):
        app = self.table.get_object_by_id(application_id)
        try:
            neutron.application_delete(request, application_id)
            LOG.debug('Deleted app %s successfully', app.name)
        except Exception as e:
            msg = _('Failed to delete application %s. Details: %s')
            LOG.info(msg, application_id, e.message)
            redirect = reverse("horizon:project:applications:index")
            usrmsg = _('Failed to delete application %s. Details: %s')
            exceptions.handle(request, usrmsg % (app.name, e.message),
                              redirect=redirect)


class CreateApplication(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Application")
    url = "horizon:project:applications:create"
    classes = ("ajax-modal",)
    icon = "plus"

    def get_link_url(self, datum=None):
        if self.table.kwargs.get('app_domain_id'):
            return reverse(
                "horizon:project:application_domains:createApplication",
                args=(self.table.kwargs['app_domain_id'],))
        else:
            return reverse("horizon:project:applications:create")


class EditApplication(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Application")
    url = "horizon:project:applications:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, datum=None):
        if self.table.kwargs.get('app_domain_id'):
            return reverse(
                "horizon:project:application_domains:updateApplication",
                args=(self.table.kwargs['app_domain_id'], datum['id']))
        else:
            return reverse("horizon:project:applications:update",
                           args=(self.table.get_object_id(datum),))


def get_domain_link(application):
    return reverse('horizon:project:application_domains:detail',
                   args=(application['associateddomainid'],))


class ApplicationsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:applications:detail')
    id = tables.Column("id",
                       verbose_name=_("ID"),
                       link='horizon:project:applications:detail')
    domain = tables.Column("associateddomainid",
                           verbose_name=_("Domain"),
                           link=get_domain_link)

    class Meta:
        name = "applications"
        verbose_name = _("Applications")
        table_actions = (CreateApplication, DeleteApplication)
        row_actions = (EditApplication, DeleteApplication)
        hidden_title = False
