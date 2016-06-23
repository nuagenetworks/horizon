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

horizon.instances.generate_networklist_html = function() {
  var $available_networks = $("#available_network");
  var $selected_network = $("#selected_network");
  var $submit_networks = $("#id_network");
  $submit_networks.parent().parent().hide();

  var updateForm = function() {
    var lists = $submit_networks.find("li").attr('data-index',100);
    var selected_networks = $("#selected_network").find("> li").map(function(){
      return $(this).attr("name");
    });
    $submit_networks.find("input:checkbox").removeAttr('checked');
    selected_networks.each(function(index, value){
      $submit_networks.find("input:checkbox[value=" + value + "]")
        .prop('checked', true)
        .parents("li").attr('data-index',index);
    });
    $submit_networks.find("ul").html(
      lists.sort(function(a,b){
        if( $(a).data("index") < $(b).data("index")) { return -1; }
        if( $(a).data("index") > $(b).data("index")) { return 1; }
        return 0;
      })
    );
  };
  $("#networkListSortContainer").show();
  $("#networkListIdContainer").show();
  horizon.instances.init_network_list();
  // Make sure we don't duplicate the networks in the list
  $available_networks.empty();
  $.each(horizon.instances.networks_available, function(index, value){
    $available_networks.append(horizon.instances.generate_network_element(value.name, value.id, value.value));
  });
  // Make sure we don't duplicate the networks in the list
  $selected_network.empty();
  $.each(horizon.instances.networks_selected, function(index, value){
    $selected_network.append(horizon.instances.generate_network_element(value.name, value.id, value.value));
  });
  $(".networklist > li > a.btn").click(function(e){
    var $this = $(this);
    e.preventDefault();
    e.stopPropagation();
    if($this.parents("ul#available_network").length > 0) {
      $this.parent().appendTo($selected_network);
    } else if ($this.parents("ul#selected_network").length > 0) {
      $this.parent().appendTo($available_networks);
    }
    updateForm();
  });
  if ($submit_networks.find("> div.form-group.error").length > 0) {
    var errortext = $submit_networks.find("> div.form-group.error span.help-block").text();
    $("#selected_network_label").before($('<div class="dynamic-error">').html(errortext));
  }
  $(".networklist").sortable({
    connectWith: "ul.networklist",
    placeholder: "ui-state-highlight",
    distance: 5,
    start:function(e,info){
      $selected_network.addClass("dragging");
    },
    stop:function(e,info){
      $selected_network.removeClass("dragging");
      updateForm();
    }
  }).disableSelection();
};

horizon.instances.network_workflow_init = function(modal) {
  horizon.instances.generate_networklist_html();
};
