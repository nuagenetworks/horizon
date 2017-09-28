/*
 * # Copyright 2015 Alcatel-Lucent USA Inc.
 * #
 * # Licensed under the Apache License, Version 2.0 (the "License"); you may
 * # not use this file except in compliance with the License. You may obtain
 * # a copy of the License at
 * #
 * #    http://www.apache.org/licenses/LICENSE-2.0
 * #
 * # Unless required by applicable law or agreed to in writing, software
 * # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * # License for the specific language governing permissions and limitations
 * # under the License.
 */

/*Class for dropdowns that must trigger another dropdown to be
 filled with data from an Ajax call.
 param $source: The jquery object of the <select> being the trigger.
 param next: A NuageLinkedSelect who should be updated when the $source
    is triggered ($source.change).
 param ajax_url: The ajax command used to fill the $source with data.
 param load_data: function executed to populate dropdown. Defaults to loading
    data via ajax using ajax_url
 param qparams: A function that returns a json object that should be send as
    data. This function takes 1 parameter, which is the value of the previous
    <select>
 param pre_trigger: A function which will be executed before Ajax
    call happens. This function can return false or true to cancel or
    continue. Default null. No function parameters. Use 'this' to access
    the NuageLinkedSelect object.
 param data_to_opts: A function that receives the <select> options and the
    json data as input. It is up to the function how to turn the data into
    <option>s
 param opt_name: A function that turns the object from the Ajax call into a
     String to be used as name for the <Option>. Default is ajax-obj.name.
     One function parameter: a single Ajax object.
 param opt_val: A function that turns the object from the Ajax call into a
     String to be used as value for the <Option>. Default is ajax-obj.id.
     One function parameter: a single Ajax object.
 */

ajax_load_data = function(param) {
  if (this.ajax_url == null) {
    return
  }
  var self = this;
  var data = {};
  if (this.qparams)
    data = this.qparams(param);

  var img = document.createElement("img");
  img.src = STATIC_URL +"dashboard/img/spinner.gif";
  this.$source.parent().before(img);

  $.ajax({
    type: 'GET',
    url: this.ajax_url,
    data: data,
    dataType: 'json',
    async: true,
    success: function (data) {
      self.data = data;
      self.show_page(0);
    },
    complete: function() {
      img.remove();
      if (self.callback) {
        self.callback();
      }
    }
  });
};

function NuageLinkedSelect(data) {
  this.$source = data['$source'];
  this.next = data['next'];
  this.ajax_url = data['ajax_url'];
  this.load_data = data['load_data'] || ajax_load_data;
  this.qparams = data['qparams'];
  this.pre_trigger = data['pre_trigger'];
  this.data_to_opts = data['data_to_opts'];
  this.opt_name = data['opt_name'] || function(obj){
    return obj.name;
  };
  this.opt_val = data['opt_val'] || function(obj){
    return obj.id;
  };
  this.page_size = data['page_size'] || 15;
  this.callback = data['callback']
  this.page = 0;
  this.data = null;

  var self = this;
  this.$source.change(function() {
    if (self.next) {
      self.next.hide();
      self.next.hide_next();
    }

    var opt = self.get_opt();
    if (!opt.custom && self.pre_trigger) {
      var result = self.pre_trigger();
      if (!result)
        return;
    }

    if (!opt.custom && self.next) {
      if (self.next.load_data != null)
        self.next.load_data(self.$source.val());
      self.next.show();
    } else if (opt.custom_func) {
      opt.custom_func();
    }
  });
  this.get_opts()[0].custom = true;
}

NuageLinkedSelect.prototype.hide_next = function() {
  if (this.next) {
    this.next.hide();
    this.next.hide_next();
  }
};

NuageLinkedSelect.prototype.hide = function() {
  if (this.ajax_url) { //if data is ajax-loaded > clear data on hide.
    this.clear_opts();
  }
  this.$source.parent().parent().hide();
};

NuageLinkedSelect.prototype.show = function() {
  this.$source.prop("selectedIndex", 0)
  this.$source.parent().parent().show();
};

NuageLinkedSelect.prototype.show_page = function(page) {
  this.clear_opts();
  var opts = this.get_opts();
  var page_data = this.data.slice(this.page_size * page,
      this.page_size * page + this.page_size);
  if (!this.data_to_opts) {
    for (var i=0 ; i<page_data.length ; i++) {
      var obj =page_data[i];
      var opt = new Option(this.opt_name(obj), this.opt_val(obj));
      opt.obj = obj;
      opts[opts.length] = opt;
    }
  } else {
    this.data_to_opts(opts, page_data)
  }
  this.page = page;

  var select = this.$source[0];
  if (page > 0) {
    var opt = new Option('< Previous', '');
    opt.custom = true;
    var self = this;
    opt.custom_func = function() {
      self.show_page(self.page-1)
    };
    select.insertBefore(opt, select[0].nextSibling);
    select.add(opt, 1);
  }
  if (page+1 < this.data.length / this.page_size) {
    var opt = new Option('Next >', '');
    opt.custom = true;
    var self = this;
    opt.custom_func = function() {
      self.show_page(self.page+1)
    };
    select.add(opt);
  }
};

NuageLinkedSelect.prototype.clear_opts = function() {
  var firstOption = this.get_opts()[0];
  this.$source.empty();
  var options = this.get_opts();
  options[0] = firstOption;
};

NuageLinkedSelect.prototype.get_opts = function() {
  return this.$source[0].options;
};

NuageLinkedSelect.prototype.get_opt = function() {
  return this.$source.find('option:selected')[0]
};