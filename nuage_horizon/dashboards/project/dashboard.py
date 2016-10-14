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
from django.utils.translation import ugettext_lazy as _

import horizon


class GatewayPanels(horizon.PanelGroup):
    slug = "gateway"
    name = _("Gateway")
    panels = ('gateways', "gateway_vlans")


class ApplicationPanels(horizon.PanelGroup):
    slug = "application_designer"
    name = _("Application Designer")
    panels = ('application_domains',
              'applications',
              'application_services')


project = horizon.get_dashboard('project')

gw_panel = GatewayPanels(project, panels=GatewayPanels.panels)
app_panel = ApplicationPanels(project, panels=ApplicationPanels.panels)

panel_groups = project._panel_groups
panel_groups[GatewayPanels.slug] = gw_panel
panel_groups[ApplicationPanels.slug] = app_panel
