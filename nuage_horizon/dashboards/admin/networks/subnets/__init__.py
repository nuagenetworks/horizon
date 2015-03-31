from django.conf.urls import url

from nuage_horizon.dashboards.admin.networks.subnets import views
from openstack_dashboard.dashboards.admin.networks import urls


def should_keep(pattern, name):
    return pattern.name != name if hasattr(pattern, 'name') else True


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'
urls.urlpatterns = [pat for pat in urls.urlpatterns if
                    should_keep(pat, 'addsubnet')]

urls.urlpatterns.append(
    url(NETWORKS % 'subnets/create',views.CreateView.as_view(), name='addsubnet')
)