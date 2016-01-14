Nuage Horizon (OpenStack Dashboard)
===================================
Horizon Extension for Nuage Networks

Activate Plugin
---------------
- Pull upstream Horizon (currently Kilo master).
- Have nuage_horizon available on the python path, or add it to the OpenStack
  Horizon folder.
- Edit openstack_dashboard/local/local_settings.py to suit your OpenStack.
- In local_settings.py edit the HORIZON_CONFIG variable. Add
  **'customization_module': 'nuage_horizon.customization'**
  to the variable.
- System dependant configuration may be required. See Apache section below.
- Start Horizon.

Apache
------
Note:

- Paths to files may be different. It is dependant on the system in use.
- When the root of horizon is just '/' (It often is /dashboard) this may not be required.

An alias should be added to horizon's config file in apache.
The path could be "/etc/apache2/sites-enabled/horizon.conf"

The alias to add is:

Alias /**<webapp-root>**/static/nuage **<nuage_horizon-install-path>**/static

This is an example alias to be used when horizon is running at <ip>:<port>/dashboard for horizon installed with devstack and nuage_horizon package installed in /opt/stack as well:

Alias /dashboard/static/nuage /opt/stack/horizon/nuage_horizon/static


There probably is a pre-existing alias: Alias /dashboard/static /opt/stack/horizon/static. The Nuage alias should be added before this one.

