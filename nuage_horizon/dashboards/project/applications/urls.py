from django.conf.urls import patterns
from django.conf.urls import url
from django.conf.urls import include

from nuage_horizon.dashboards.project.applications import views as app_views
from nuage_horizon.dashboards.project.applications.tiers \
    import views as tier_views
from nuage_horizon.dashboards.project.applications.flows \
    import views as flow_views
from nuage_horizon.dashboards.project.applications.tiers \
    import urls as tier_urls
from nuage_horizon.dashboards.project.applications.flows \
    import urls as flow_urls


APPLICATION = r'^(?P<application_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^$', app_views.IndexView.as_view(), name='index'),
    url(r'^create/$', app_views.CreateView.as_view(), name='create'),
    url(APPLICATION % '$', app_views.DetailView.as_view(), name='detail'),
    url(APPLICATION % 'update', app_views.UpdateView.as_view(), name='update'),
    url(APPLICATION % 'tiers/create', tier_views.CreateView.as_view(),
        name='createtier'),
    url(APPLICATION % 'flows/create', flow_views.CreateView.as_view(),
        name='createflow'),
    url(r'^tiers/', include(tier_urls, namespace='tiers')),
    url(r'^flows/', include(flow_urls, namespace='flows')),)
