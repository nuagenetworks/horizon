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

var $app_select = $('#id_application_id');
var $submit_tiers = $('#id_tier_id');
var $available_tiers = $('#available_tier');
var $selected_tier = $('#selected_tier');
var $hidden_tiers = $('#id_hidden_tiers');

function addToSubmitFormInput(i, tier) {
  var input = document.createElement('input');
  input.setAttribute('id', 'id_tier_id_' + i);
  input.setAttribute('name', 'tier_id');
  input.setAttribute('type', 'checkbox');
  input.setAttribute('value', tier.id);

  $submit_tiers.append(input);
}

function addToAvailableTiers(tier) {
  var li = document.createElement('li');
  li.setAttribute('name', tier.id);
  li.innerHTML = tier.name;

  var em = document.createElement('em');
  em.setAttribute('class', 'tier_id');
  em.innerHTML = '(' + tier.id + ')';

  var a = document.createElement('a');
  a.setAttribute('class', 'btn btn-primary');

  li.appendChild(em);
  li.appendChild(a);

  $available_tiers.append(li);
}

$app_select.change(function () {
  $available_tiers.empty();
  $selected_tier.empty();
  $submit_tiers.empty();
  var app_id = this.value;
  if (!app_id)
    return;

  var img = document.createElement("img");
  img.src = STATIC_URL + "dashboard/img/spinner.gif";
  $submit_tiers.parent().before(img);

  $.ajax({
    type: 'GET',
    url: STATIC_URL + '../project/instances/listTiers',
    data: {'app_id': app_id},
    dataType: 'json',
    async: true,
    success: function (data) {
      for (var i=0 ; i<data.length ; i++) {
        var tier = data[i];
        addToAvailableTiers(tier);
        addToSubmitFormInput(i, tier);
      }
      horizon.instances.generate_tierlist_html();
      debugger;
      if ($hidden_tiers.val()) {
        // Handle form returning after invalid form Submit
        $.each($hidden_tiers.val().split('____'), function(index, value){
          $('li[name="'+value+'"] > a').trigger('click');
        });
        $hidden_tiers.val('');
      }
    },
    complete: function () {
      img.remove();
    }
  });
});


// Handle form returning after invalid form Submit
if ($app_select.val()) {
  $app_select.trigger('change');
}