debugger;

$type = $("#id_type");
$name = $("#id_name");
$desc = $("#id_description");
$cidr = $("#id_cidr");
$fip = $("#id_fip_pool");

type_show = {
  '': [],
  'STANDARD': [$name, $desc, $cidr, $fip],
  'NETWORK_MACRO': [$name, $desc, $cidr],
  'APPLICATION': [$name, $desc],
  'APPLICATION_EXTENDED_NETWORK': [$name, $desc]
};

function hide_all() {
  hide($name, $desc, $desc, $cidr, $fip);
}

function hide() {
  for (var i=0 ; i<arguments.length ; i++) {
    arguments[i].parent().parent().hide();
  }
}

function show() {
  for (var i = 0; i < arguments.length; i++) {
    arguments[i].parent().parent().show();
  }
}

function type_set() {
  hide_all();
  var to_show = type_show[this.value];
  for (var i=0 ; i<to_show.length ; i++) {
    show(to_show[i]);
  }
}

$type.change(type_set);

type_set.call($type[0]);
