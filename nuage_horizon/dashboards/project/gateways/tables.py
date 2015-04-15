import logging

from django.utils.translation import ugettext_lazy as _
from horizon import tables


LOG = logging.getLogger(__name__)


class GatewaysTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link='horizon:project:gateways:detail')
    description = tables.Column("description", verbose_name=_("Description"))
    type = tables.Column("type", verbose_name=_("Type"))
    status = tables.Column("status", verbose_name=_("Status"))
    system_id = tables.Column("systemid", verbose_name=_("System Id"))

    class Meta:
        name = "gateways"
        verbose_name = _("Gateways")
