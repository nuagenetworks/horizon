import os

from horizon import loaders
from . import views
from . import forms
from . import urls
from . import tabs


routers_dir = os.path.dirname(__file__)
template_dir = os.path.join(routers_dir, "templates")
loaders.panel_template_dirs['nuage/routers'] = template_dir