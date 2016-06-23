from django.conf.urls import patterns
from django.conf.urls import url

from nuage_horizon.dashboards.project.applications.flows \
    import views as flow_views


FLOW = r'^(?P<flow_id>[^/]+)/%s'


urlpatterns = patterns(
    '',
    url(r'^create/$', flow_views.CreateView.as_view(), name='create'),
    url(FLOW % '$', flow_views.DetailView.as_view(), name='detail'),
    url(FLOW % 'update', flow_views.UpdateView.as_view(), name='update'),)
