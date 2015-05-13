import logging

from horizon import tables
from horizon import exceptions

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext_lazy

from openstack_dashboard import policy

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__) \

TIER_TYPE_DICT = {'STANDARD': 'Application Tier',
                  'NETWORK_MACRO': 'Network Macro',
                  'APPLICATION': 'Current Application',
                  'APPLICATION_EXTENDED_NETWORK': "Application's Domain"}


class DeleteTier(policy.PolicyTargetMixin, tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Tier",
            u"Delete Tiers",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Tier",
            u"Deleted Tiers",
            count
        )

    policy_rules = (("tier", "delete_tier"),)

    def delete(self, request, tier_id):
        tier = self.table.get_object_by_id(tier_id)
        try:
            neutron.tier_delete(request, tier_id)
            LOG.debug('Deleted tier %s successfully', tier.name)
        except Exception as e:
            msg = _('Failed to delete tier %s. Details: %s')
            LOG.info(msg, tier_id, e.message)
            redirect = reverse('horizon:project:applications:detail',
                               args=[tier.associatedappid])
            exceptions.handle(request, msg % (tier_id, e.message),
                              redirect=redirect)


class CreateTier(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Tier")
    url = "horizon:project:applications:createtier"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("tier", "create_tier"),)

    def get_link_url(self, datum=None):
        app_id = self.table.kwargs['application_id']
        return reverse(self.url, args=(app_id,))


class EditTier(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Tier")
    url = "horizon:project:applications:tiers:update"
    classes = ("ajax-modal",)
    icon = "pencil"

    def get_link_url(self, tier=None):
        return reverse(self.url, args=(tier.id,))


def get_type(tier):
    return TIER_TYPE_DICT[tier.type]


class TiersTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:applications:tiers:detail')
    type = tables.Column(get_type, verbose_name=_("type"))

    class Meta:
        name = "tiers"
        verbose_name = _("Tiers")
        table_actions = (CreateTier, DeleteTier)
        row_actions = (EditTier, DeleteTier)
        hidden_title = False