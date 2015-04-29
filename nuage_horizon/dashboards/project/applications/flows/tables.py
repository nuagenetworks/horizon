import logging

from horizon import tables
from horizon import exceptions

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__)


class DeleteFlow(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Flow",
            u"Delete Flows",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Flow",
            u"Deleted Flows",
            count
        )

    def delete(self, request, flow_id):
        flow = self.table.get_object_by_id(flow_id)
        try:
            neutron.flow_delete(request, flow_id)
            LOG.debug('Deleted flow %s successfully', flow.name)
        except Exception as e:
            msg = _('Failed to delete flow %s. Details: %s')
            LOG.info(msg, flow_id, e.message)
            redirect = reverse('horizon:project:applications:detail',
                               args=[flow.associatedappid])
            exceptions.handle(request, msg % (flow_id, e.message),
                              redirect=redirect)


class CreateFlow(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Flow")
    url = "horizon:project:applications:createflow"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("flow", "create_flow"),)

    def get_link_url(self, datum=None):
        app_id = self.table.kwargs['application_id']
        return reverse(self.url, args=(app_id,))


class EditFlow(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Flow")
    url = "horizon:project:applications:flows:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, flow=None):
        return reverse(self.url, args=(flow.id,))


def get_orig_tier_name(flow):
    return flow['origin_tier']['name']


def get_dest_tier_name(flow):
    return flow['dest_tier']['name']


def get_orig_tier_link(flow):
    tier_id = flow['origin_tier']['id']
    return reverse('horizon:project:applications:tiers:detail', args=(tier_id,))


def get_dest_tier_link(flow):
    tier_id = flow['dest_tier']['id']
    return reverse('horizon:project:applications:tiers:detail', args=(tier_id,))


class FlowsTable(tables.DataTable):
    origin_tier = tables.Column(get_orig_tier_name,
                                verbose_name=_("From"),
                                link=get_orig_tier_link)
    dest_tier = tables.Column(get_dest_tier_name,
                              verbose_name=_("To"),
                              link=get_dest_tier_link)

    class Meta:
        name = "flows"
        verbose_name = _("Flows")
        table_actions = (CreateFlow, DeleteFlow)
        row_actions = (EditFlow, DeleteFlow)
        hidden_title = False