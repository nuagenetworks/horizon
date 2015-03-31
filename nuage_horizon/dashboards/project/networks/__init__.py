import os

from django.conf.urls import url

from horizon import loaders
from nuage_horizon.dashboards.project.networks import views
from openstack_dashboard.dashboards.project.networks import urls

network_dir = os.path.dirname(__file__)
template_dir = os.path.join(network_dir, "templates")
loaders.panel_template_dirs['nuage/networks'] = template_dir


def should_keep(pattern, name):
    return pattern.name != name if hasattr(pattern, 'name') else True


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'create')]
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'detail')]

urls.urlpatterns.append(
    url(r'^create$', views.NuageCreateView.as_view(), name='create'))
urls.urlpatterns.append(
    url(NETWORKS % 'detail', views.NuageDetailView.as_view(), name='detail'))

