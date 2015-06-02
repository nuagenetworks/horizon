/*
 * Copyright 2015 Alcatel-Lucent USA Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may
 * not use this file except in compliance with the License. You may obtain
 * a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */
$(document).ready(function(){
  var KEY_ALT=18;
  var KEY_BACKSPACE=8;
  var KEY_CTRL=17;
  var KEY_END=35;
  var KEY_ENTER=13;
  var KEY_HOME=36;
  var KEY_LEFT=37;
  var KEY_RIGHT=39;
  var KEY_SHIFT=16;
  var KEY_TAB=9;

  var special_keys = [KEY_ALT, KEY_BACKSPACE, KEY_CTRL, KEY_END, KEY_ENTER,
                      KEY_HOME, KEY_LEFT, KEY_RIGHT, KEY_SHIFT, KEY_TAB];
  var fields = $('.nuage-mac input');
  var mac_regex = new RegExp('[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:' +
                             '[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}');


  /**
   * On key press, go to the next input field when the current ons is filled.
   * Unless the key pressed was one of special_keys.
   */
  fields.keyup(function () {
    var $this = $(this);
    var content = $this.val();
    if (content.length == 2  && special_keys.indexOf(event.which) == -1) {
      $this.next().focus();
    }
  });

  fields.focus(function(){
    $(this).select();
  });

  /**
   * When pressing backspace, arrow-left, arrow-right, home > set focus to the
   * correct input field.
   */
  fields.keydown(function () {
    var $this = $(this);
    if (event.which == KEY_BACKSPACE && $this[0].selectionStart == 0
        && $this[0].selectionEnd == 0 ) {
      $this.prev().focus();
      return false;
    }
    if (event.which == KEY_LEFT && $this[0].selectionStart == 0 ) {
      $this.prev().focus();
      return false;
    }
    if (event.which == KEY_RIGHT
        && $this[0].selectionStart == $this[0].value.length ) {
      $this.next().focus();
      return false;
    }
    if (event.which == KEY_END) {
      focus_last();
      return true;
    }
    if (event.which == KEY_HOME) {
      $(fields[0]).focus();
      return true;
    }
  });

  /**
   * When clicking in the space to the right of the <input> fields but still in
   * the div, set cursor to the correct input field.
   */
  $('.nuage-mac').click(function(event){
    if ($(event.target).is("div")) {
      focus_last()
    }
  });

  /**
   * When pasting a valid mac-address, fill in each input field.
   * Other than that, disable pasting.
   */
  fields.bind('paste', function(){
    var pasted = event.clipboardData.getData('text/plain');
    if (!pasted.match(mac_regex))
      return false;

    pasted = pasted.split(":").join("");
    for (var i=1 ; i<=12 && i < pasted.length ; i+=2) {
      var index = Math.floor((i+1)/2) -1;
      fields[index].value = pasted.charAt(i-1) + pasted.charAt(i)
    }
    $(fields[5]).focus();
    return false
  });

  /**
   * Focus the first field that is not yet filled.
   */
  function focus_last() {
    for (var i=0 ; i<fields.length ; i++) {
      if (fields[i].value.length < 2) {
        $(fields[i]).focus();
        return
      }
    }
    $(fields[fields.length-1]).focus();
  }
});