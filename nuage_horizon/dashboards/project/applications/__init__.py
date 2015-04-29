import os

from . import panel
from horizon import loaders


app_dir = os.path.dirname(__file__)
template_dir = os.path.join(app_dir, "templates")
loaders.panel_template_dirs['nuage/applications'] = template_dir
