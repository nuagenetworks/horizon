from openstack_dashboard.dashboards.project.routers import views as original
from nuage_horizon.dashboards.project.routers import forms


class NuageUpdateView(original.UpdateView):
    form_class = forms.NuageRouterUpdateForm

    def get_initial(self):
        router = self._get_object()
        initial = {'router_id': router['id'],
                   'tenant_id': router['tenant_id'],
                   'name': router['name'],
                   'rd': router['rd'],
                   'rt': router['rt'],
                   'tunnel_type': router['tunnel_type'],
                   'admin_state': router['admin_state_up'],
                   'snat_enabled':
                       (router.get('external_gateway_info') or {}).get(
                           'enable_snat'),
                   'external_gateway_info':
                       router.get('external_gateway_info')}
        if hasattr(router, 'distributed'):
            initial['mode'] = ('distributed' if router.distributed
                               else 'centralized')
        if hasattr(router, 'ha'):
            initial['ha'] = router.ha
        return initial

original.CreateView.form_class = forms.NuageRouterCreateForm
