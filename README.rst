Nuage Horizon (OpenStack Dashboard)
===================================
Horizon Extension for Nuage Networks

How to install:

Activate Plugin
---------------
- Make sure horizon is installed.
- Clone and python install (setup.py) nuage-horizon.
- In horizon project, edit openstack_dashboard/local/local_settings.py.
  Add the line: HORIZON_CONFIG["customization_module"] = "nuage_horizon.customization"

Apache
------

- An alias should be added to horizon's config file in apache.
  The path could be "/etc/apache2/sites-enabled/horizon.conf"

  Alias /**<webapp-root>**/static/nuage **<nuage_horizon-install-path>**/static

  On a devstack setup this may look like:
  Alias /dashboard/static/nuage /opt/stack/nuage-horizon/nuage_horizon/static

  There probably is a pre-existing alias: Alias /dashboard/static /opt/stack/horizon/static.
  The Nuage alias should be added before this one.

  Adjust the directory permissions also by adding the following:

  <Directory /opt/stack/nuage-horizon/>
      Options Indexes FollowSymLinks MultiViews
      AllowOverride None
      # Apache 2.4 uses mod_authz_host for access control now (instead of
      #  "Allow")
      <IfVersion < 2.4>
          Order allow,deny
          Allow from all
      </IfVersion>
      <IfVersion >= 2.4>
          Require all granted
      </IfVersion>
  </Directory>

- Restart service apache2.






