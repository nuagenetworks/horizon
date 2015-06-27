#!/bin/bash
# 
# Name:
#
# Author:Chao Zhang
# Author:Nicolas Ochem
#
# Email: chao.zhang1@alcatel-lucent.com
#
## Description: This the nuage horizon building script for
# debian/ubuntu debs
#
set -e
OVS_BUILD_NUMBER=$(echo $BUILD_NAME | sed "s/^.*-\(.*\)$/\1/")

# HACK HACK HACK
# We do not want to depend on the dashboard do build rpm so I remove the dependency in setup.cfg
sed -i '/\[global\]/d' setup.cfg
sed -i '/.*setup.*hook.*/d' setup.cfg

python setup.py egg_info

DEBEMAIL="Nuage Networks <info@nuagenetworks.net>" dch -b --newversion \
            ${OVS_BUILD_NUMBER}-nuage-kilo "Jenkins build" --distribution $(lsb_release --codename --short)

debuild -b -kinfo@nuagenetworks.net

if [ ! $? -eq 0 ]
then
    echo "debian build failed"
    exit 1
fi

mv ../neutron-plugin-nuage* .
if [ -n "$BUILD_NAME" ]
then
    dpkg-sig -k 83496517 -s builder neutron-plugin-nuage_*.changes
fi

exit 0
