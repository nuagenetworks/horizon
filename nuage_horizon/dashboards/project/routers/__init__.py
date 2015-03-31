import os

from horizon import loaders
from django.conf.urls import url
from openstack_dashboard.dashboards.project.routers import urls
from openstack_dashboard.dashboards.project.routers import views as def_views
from nuage_horizon.dashboards.project.routers import views
from . import forms

def_views.CreateView.form_class = forms.NuageRouterCreateForm

routers_dir = os.path.dirname(__file__)
template_dir = os.path.join(routers_dir, "templates")
loaders.panel_template_dirs['nuage/routers'] = template_dir

def_views.DetailView.template_name = 'nuage/routers/detail.html'


ROUTER_URL = r'^(?P<router_id>[^/]+)/%s'


def should_keep(pattern):
    return pattern.name != 'update' if hasattr(pattern, 'name') else True

urls.urlpatterns = [pat for pat in urls.urlpatterns if should_keep(pat)]

urls.urlpatterns.append(url(ROUTER_URL % 'update',
                            views.NuageUpdateView.as_view(),
                            name='update'))