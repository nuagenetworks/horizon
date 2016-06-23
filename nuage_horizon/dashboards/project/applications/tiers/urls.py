from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.applications.tiers \
    import views as tier_views


TIER = r'^(?P<tier_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^create/$', tier_views.CreateView.as_view(), name='create'),
    url(TIER % '$', tier_views.DetailView.as_view(), name='detail'),
    url(TIER % 'update', tier_views.UpdateView.as_view(), name='update'),)
