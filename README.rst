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
- Start Horizon.