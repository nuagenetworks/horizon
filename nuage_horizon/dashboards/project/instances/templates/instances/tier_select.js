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

horizon.instances.generate_tierlist_html = function() {
  var $available_tiers = $("#available_tier");
  var $selected_tier = $("#selected_tier");
  var $submit_tiers = $("#id_tier_id");
  var $hidden_tiers = $("#id_hidden_tiers");
  $submit_tiers.parent().parent().hide();

  var updateForm = function() {
    var lists = $submit_tiers.find("li").attr('data-index',100);
    var selected_tiers = $("#selected_tier").find("> li").map(function(){
      return $(this).attr("name");
    });
    $submit_tiers.find("input:checkbox").removeAttr('checked');
    var all_tiers = '';
    selected_tiers.each(function(index, value){
      $submit_tiers.find("input:checkbox[value=" + value + "]")
        .prop('checked', true)
        .parents("li").attr('data-index',index);
      all_tiers += value + '____'
    });
    if (all_tiers) {
      $hidden_tiers.val(all_tiers.substring(0, all_tiers.length-4));
    }
    $submit_tiers.find("ul").html(
      lists.sort(function(a,b){
        if( $(a).data("index") < $(b).data("index")) { return -1; }
        if( $(a).data("index") > $(b).data("index")) { return 1; }
        return 0;
      })
    );
  };
  $(".tierlist > li > a.btn").click(function(e){
    var $this = $(this);
    e.preventDefault();
    e.stopPropagation();
    if($this.parents("ul#available_tier").length > 0) {
      $this.parent().appendTo($selected_tier);
    } else if ($this.parents("ul#selected_tier").length > 0) {
      $this.parent().appendTo($available_tiers);
    }
    updateForm();
  });
  if ($submit_tiers.find("> div.form-group.error").length > 0) {
    var errortext = $submit_tiers.find("> div.form-group.error span.help-block").text();
    $("#selected_tier_label").before($('<div class="dynamic-error">').html(errortext));
  }
  $(".tierlist").sortable({
    connectWith: "ul.tierlist",
    placeholder: "ui-state-highlight",
    distance: 5,
    start:function(e,info){
      $selected_tier.addClass("dragging");
    },
    stop:function(e,info){
      $selected_tier.removeClass("dragging");
      updateForm();
    }
  }).disableSelection();
};

horizon.instances.tier_workflow_init = function(modal) {
  horizon.instances.generate_tierlist_html();
};
