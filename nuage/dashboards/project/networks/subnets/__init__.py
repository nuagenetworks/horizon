from django.conf.urls import url
from nuage.dashboards.project.networks.subnets import views

from openstack_dashboard.dashboards.project.networks import urls


NETWORKS = r'^(?P<network_id>[^/]+)/%s$'


def should_keep(pattern):
    return (pattern.name != 'addsubnet' and pattern.name != 'editsubnet') \
        if hasattr(pattern, 'name') else True

urls.urlpatterns = [pat for pat in urls.urlpatterns if should_keep(pat)]

urls.urlpatterns.append(url(NETWORKS % 'subnets/create',
                            views.CreateView.as_view(),
                            name='addsubnet'))
urls.urlpatterns.append(
    url(r'^(?P<network_id>[^/]+)/subnets/(?P<subnet_id>[^/]+)/update$',
        views.UpdateView.as_view(), name='editsubnet'))



