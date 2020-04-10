#!/bin/bash

# Copyright 2019 NOKIA
#
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

function configure_nuage_horizon {
    local local_settings=$HORIZON_DIR/openstack_dashboard/local/local_settings.py
    _horizon_config_set $local_settings "" HORIZON_CONFIG[\'customization_module\'] \"nuage_horizon.customization\"
    local horizon_conf=$(apache_site_config_for horizon)
    if is_ubuntu || is_fedora || is_suse; then
       sudo sh -c "sed -i '/Alias \/dashboard\/static/i \ \ \ \ Alias $HORIZON_APACHE_ROOT/static/nuage /opt/stack/nuage-openstack-horizon/nuage_horizon/static' $horizon_conf"
       sudo sh -c "sed -i '/<Directory \/opt\/stack\/horizon/i \ \ \ \ <Directory /opt/stack/nuage-openstack-horizon/>\n        Options Indexes FollowSymLinks MultiViews\n        AllowOverride None\n        Require all granted\n    </Directory>' $horizon_conf"
    else
       exit_distro_not_supported "horizon apache configuration"
    fi
}

if [[ "$1" == "stack" ]]; then
    if [[ "$2" == "install" ]]; then
        echo_summary "Installing Nuage Horizon plugin"
        pip_install -r $NUAGE_HORIZON_DIR/requirements.txt -e $NUAGE_HORIZON_DIR -c $REQUIREMENTS_DIR/upper-constraints.txt
        if is_fedora && python3_enabled; then
          os=$(eval $"rpm -E '%{?centos:centos}%{!?centos:rhel}%{rhel}'")
          install_package "https://$os.iuscommunity.org/ius-release.rpm"
          install_package "python${PYTHON3_VERSION//./}u-mod_wsgi"
          uninstall_package "mod_wsgi"
        fi
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        configure_nuage_horizon
    fi
elif [[ "$1" == "unstack" ]]; then
        # no-op
        :
fi

