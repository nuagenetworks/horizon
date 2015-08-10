import logging

from horizon import tables
from horizon import exceptions
from horizon import messages

from django import shortcuts
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from nuage_horizon.api import neutron


LOG = logging.getLogger(__name__)


class CreateGwVlan(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Gateway Vlan")
    url = "horizon:project:gateways:ports:createvlan"
    classes = ("ajax-modal",)
    icon = "plus"
    policy_rules = (("gw_vlan", "create_gw_vlan"),)

    def allowed(self, request, gw_vlan):
        return request.user.is_superuser

    def get_link_url(self, datum=None):
        gw_port_id = self.table.kwargs['gw_port_id']
        return reverse(self.url, args=[gw_port_id])


class AssignGwVlan(tables.LinkAction):
    name = "assign"
    verbose_name = _("Assign Gateway Vlan")
    url = "horizon:project:gateway_vlans:edit"
    classes = ("ajax-modal", "btn-associate")

    def allowed(self, request, gw_vlan):
        return gw_vlan['vport'] is None


class UnassignGwVlan(tables.Action):
    name = 'unassign'
    verbose_name = _("Unassign Gateway Vlan")
    classes = ("btn-disassociate")

    def allowed(self, request, gw_vlan):
        return (gw_vlan['vport'] is None
                and gw_vlan.get('assigned') is not None
                and request.user.is_superuser)

    def single(self, table, request, gw_vlan_id):
        gw_vlan = table.get_object_by_id(gw_vlan_id)
        redirect = reverse("horizon:project:gateways:ports:detail",
                           args=[gw_vlan['gatewayport']])
        try:
            neutron.nuage_gateway_vlan_unassign(
                request,
                gw_vlan_id,
                tenant_id=gw_vlan['assigned'])
            messages.success(request, _("Unassigned Gateway Vlan"))
        except Exception:
            msg = _("Failed to unassign gateway vlan %s")
            LOG.info(msg, gw_vlan['id'])
            exceptions.handle(request, msg % gw_vlan_id, redirect=redirect)
        return shortcuts.redirect(redirect)


class DeleteVport(tables.Action):
    name = 'deleteVport'
    verbose_name = _("Delete Vport")
    classes = ("btn-danger", "btn-disassociate",)
    help_text = _("This will permanently delete the Nuage Vport.")

    def allowed(self, request, gw_vlan):
        return gw_vlan['vport'] is not None

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete vport",
            u"Delete vport",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Gateway's vport",
            u"Deleted Gateway's vports",
            count
        )

    def single(self, table, request, gw_vlan_id):
        gw_vlan = table.get_object_by_id(gw_vlan_id)
        if request.user.is_superuser:
            redirect = reverse("horizon:project:gateways:ports:detail",
                               args=[gw_vlan['gatewayport']])
        else:
            redirect = reverse("horizon:project:gateway_vlans:index")
        vport = gw_vlan.get('vport')
        try:
            if vport:
                neutron.nuage_gateway_vport_delete(request, vport['id'])
            messages.success(request, _(self.action_past(1)))
        except Exception:
            msg = _("Failed to delete Gateway's vport %s")
            LOG.info(msg, vport['id'])
            exceptions.handle(request, msg % gw_vlan_id, redirect=redirect)
        return shortcuts.redirect(redirect)


class DeleteGwVlan(tables.DeleteAction):
    def allowed(self, request, gw_vlan):
        return request.user.is_superuser

    def allowed(self, request, gw_vlan):
        return (gw_vlan and gw_vlan['vport'] is None
                and gw_vlan.get('assigned') is None
                and request.user.is_superuser)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Gateway Vlan",
            u"Delete Gateway Vlans",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Gateway Vlan",
            u"Deleted Gateway Vlans",
            count
        )

    def delete(self, request, gw_vlan_id):
        gw_vlan = self.table.get_object_by_id(gw_vlan_id)
        try:
            vport = gw_vlan.get('vport')
            if vport:
                neutron.nuage_gateway_vport_delete(request, vport['id'])
            neutron.nuage_gateway_vlan_delete(request, gw_vlan_id)
        except Exception:
            msg = _('Failed to delete Gateway Vlan %s') % gw_vlan_id
            LOG.info(msg)
            redirect = reverse("horizon:project:gateways:ports:detail",
                               args=[gw_vlan['gatewayport']])
            exceptions.handle(request, msg, redirect=redirect)


def get_subnet(gw_vlan):
    subnet = gw_vlan.get('subnet')
    if subnet:
        return subnet.get('name') + ' ' + subnet.cidr


def get_port(gw_vlan):
    port = gw_vlan.get('port')
    if port:
        return port.get('name') + ' ' + port.fixed_ips[0]['ip_address']


def get_vport_type(gw_vlan):
    vport = gw_vlan.get('vport')
    if vport:
        return vport.get('type')


def get_subnet_link(gw_vlan):
    if gw_vlan.get('subnet'):
        args = [gw_vlan['subnet']['id']]
        return reverse('horizon:project:networks:subnets:detail', args=args)


def get_port_link(gw_vlan):
    if gw_vlan.get('port'):
        args = [gw_vlan['port']['id']]
        return reverse('horizon:project:networks:ports:detail', args=args)


def get_project_link(gw_vlan):
    if gw_vlan.get('assigned'):
        args = [gw_vlan['assigned']]
        return reverse('horizon:identity:projects:detail', args=args)


class VlansTable(tables.DataTable):
    vlan = tables.Column("value", verbose_name=_("VLAN"))
    assigned = tables.Column("assigned", verbose_name=_("Assigned to"),
                             link=get_project_link)
    status = tables.Column("status", verbose_name=_("Status"))

    subnet = tables.Column(get_subnet, verbose_name=_("Subnet"),
                           link=get_subnet_link)

    port = tables.Column(get_port, verbose_name=_("Port"),
                         link=get_port_link)
    type = tables.Column(get_vport_type, verbose_name=_("Type"))

    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(VlansTable, self).__init__(request, data, needs_form_wrapper,
                                         **kwargs)
        if not request.user.is_superuser:
            del self.columns['assigned']

    def get_object_display(self, datum):
        return datum.get('value')

    class Meta:
        name = "vlans"
        verbose_name = _("Gateway Vlans")
        hidden_title = False
        table_actions = (CreateGwVlan, DeleteGwVlan)
        row_actions = (AssignGwVlan, UnassignGwVlan,
                       DeleteVport, DeleteGwVlan,)
