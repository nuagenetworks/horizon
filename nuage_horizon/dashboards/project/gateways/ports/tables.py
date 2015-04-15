import logging

from horizon import tables

from django.utils.translation import ugettext_lazy as _


LOG = logging.getLogger(__name__)


class PortsTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:gateways:ports:detail')
    description = tables.Column("description", verbose_name=_("Description"))
    vlan = tables.Column("vlan", verbose_name=_("VLAN range"))
    status = tables.Column("status", verbose_name=_("Status"))

    class Meta:
        name = "ports"
        verbose_name = _("Ports")
        hidden_title = False