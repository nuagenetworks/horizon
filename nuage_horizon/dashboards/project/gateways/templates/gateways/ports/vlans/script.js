/*
 * # Copyright 2015 Alcatel-Lucent USA Inc.
 * #
 * #    Licensed under the Apache License, Version 2.0 (the "License"); you may
 * #    not use this file except in compliance with the License. You may obtain
 * #    a copy of the License at
 * #
 * #        http://www.apache.org/licenses/LICENSE-2.0
 * #
 * #    Unless required by applicable law or agreed to in writing, software
 * #    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * #    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * #    License for the specific language governing permissions and limitations
 * #    under the License.
 */
var port_select, subnet_select, type_select, tenant_select;
port_select = new NuageLinkedSelect({
  $source: $('#id_port_id'),
  ajax_url: WEBROOT + '/project/gateway_vlans/listPorts',
  qparams: function(param){
    return {'network_id': subnet_select.get_opt().obj.network_id};
  },
  opt_name: function(port) {
    return port.name + ' - ' + port.fixed_ips[0].ip_address;
  }
});
subnet_select = new NuageLinkedSelect({
  $source: $('#id_subnet_id'),
  ajax_url: WEBROOT + '/project/gateway_vlans/listSubnets',
  qparams: function(ignored){
    if (tenant_select)
      return {'tenant_id': tenant_select.get_opt().value};
    else if ($('#id_assigned').length)
      return {'tenant_id': $('#id_assigned').val()};
    else
      return {};
  },
  next: port_select,
  opt_name: function(subnet) {
    return subnet.name + ' - ' + subnet.cidr;
  },
  pre_trigger: function() {
    return type_select.get_opt().value == 'host';
  }
});
type_select = new NuageLinkedSelect({
  $source: $('#id_type'),
  next: subnet_select
});
var $tenant_box = $('#id_assigned');
if ( $tenant_box.length && $tenant_box.is('select') ) {
  tenant_select = new NuageLinkedSelect({
    $source: $tenant_box,
    next: type_select
  });
}

if ((!tenant_select && type_select.$source.prop("selectedIndex") == 0)) {
  type_select.hide_next();
} else if (tenant_select) {
  tenant_select.hide_next();
}

if (type_select.$source.prop("selectedIndex") != 0) {
  type_select.$source.trigger("change");
}
