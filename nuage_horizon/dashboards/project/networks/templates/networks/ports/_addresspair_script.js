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
var KEY_LEFT=37;
var KEY_RIGHT=39;
var KEY_BACKSPACE=8;
var KEY_TAB=9;
var KEY_SHIFT=16;
var KEY_CTRL=17;
var KEY_ALT=18;

$(document).ready(function(){
  function focus($field) {
    if (!$field.is('input'))
      return false;
    $field.focus();
    var value = $field.val();
    $field.val('');
    $field.val(value);
    $field.select();
  }

  var fields = $('.nuage-mac input');
  fields.keyup(function () {
    var $this = $(this);
    var content = $this.val();
    if (content.length == 2
        && event.which != KEY_BACKSPACE
        && event.which != KEY_LEFT
        && event.which != KEY_RIGHT
        && event.which != KEY_TAB
        && event.which != KEY_SHIFT
        && event.which != KEY_CTRL
        && event.which != KEY_ALT) {
      focus($this.next());
    }
  });
  fields.keydown(function () {
    var $this = $(this);
    console.log(event.which);
    if (event.which == KEY_BACKSPACE && $this[0].selectionStart == 0 ) {
      focus($this.prev());
      return false;
    }
    if (event.which == KEY_LEFT && $this[0].selectionStart == 0 ) {
      focus($this.prev());
      return false;
    }
    if (event.which == KEY_RIGHT && $this[0].selectionStart == 2 ) {
      $this.next().focus();
      return false;
    }
  });

  $('.nuage-mac').click(function(event){
    if ($(event.target).is("div")) {
      for (var i=fields.length-1 ; i>=0 ; i--) {
        if (fields[i].value.length == 1) {
          focus($(fields[i]));
          return true
        }
        if (fields[i].value.length == 2 && i<fields.length-2) {
          focus($(fields[i+1]));
          return true
        }
        if (fields[i].value.length == 2){
          focus($(fields[i]));
          return true
        }
      }
      focus($(fields[0]));
    }
  });

  var mac_regex = new RegExp('[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:' +
                             '[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}');
  $('.nuage-mac input').bind('paste', function(){
    var pasted = event.clipboardData.getData('text/plain');
    if (!pasted.match(mac_regex))
      return;

    pasted = pasted.split(":").join("");
    for (var i=1 ; i<=12 && i < pasted.length ; i+=2) {
      var index = Math.floor((i+1)/2) -1;
      fields[index].value = pasted.charAt(i-1) + pasted.charAt(i)
    }
    $(fields[5]).focus();
  });
  console.log('debug');
});