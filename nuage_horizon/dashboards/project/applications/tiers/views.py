from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized

from nuage_horizon.api import neutron

from nuage_horizon.dashboards.project.applications.tiers \
    import forms as tier_forms
from nuage_horizon.dashboards.project.applications.tiers \
    import tables as tier_tables
from openstack_dashboard.api import nova


class CreateView(forms.ModalFormView):
    form_class = tier_forms.CreateForm
    form_id = "create_tier_form"
    modal_header = _("Create Tier")
    template_name = 'nuage/applications/tiers/create.html'
    success_url = 'horizon:project:applications:detail'
    failure_url = 'horizon:project:applications:detail'
    submit_url = 'horizon:project:applications:createtier'
    page_title = _("Create Tier")
    submit_label = _("Create Tier")

    def get_success_url(self):
        return reverse(self.success_url, args=(self.kwargs['application_id'],))

    @memoized.memoized_method
    def _get_object(self):
        try:
            app_id = self.kwargs["application_id"]
            return neutron.application_get(self.request, app_id)
        except Exception:
            redirect = reverse(self.failure_url, args=[app_id])
            msg = _("Unable to retrieve application.")
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['application'] = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(self._get_object().id,))
        return context

    def get_initial(self):
        app = self._get_object()
        return {"application_id": self.kwargs['application_id'],
                "application_name": app.name}


class DetailView(tables.DataTableView):
    table_class = tier_tables.InstancesTable
    template_name = 'project/applications/tiers/detail.html'
    page_title = _("Tier Details")

    def get_data(self):
        tier_id = self.kwargs['tier_id']
        appdports = neutron.appdport_list(self.request,
                                          name='appdport_%s' % tier_id)
        instances = []
        for port in appdports:
            server = nova.server_get(self.request, port['device_id'])
            instances.append(server)
        return instances

    @memoized.memoized_method
    def _get_data(self):
        try:
            tier = neutron.tier_get(self.request,
                                    self.kwargs['tier_id'])
        except Exception:
            redirect = reverse('horizon:project:applications:index')
            msg = (_('Unable to retrieve details for tier "%s".')
                   % self.kwargs['tier_id'])
            exceptions.handle(self.request, msg, redirect=redirect)
        return tier

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        tier = self._get_data()
        context['tier'] = tier
        table = tier_tables.TiersTable(self.request)
        context["actions"] = table.render_row_actions(tier)
        return context


class UpdateView(forms.ModalFormView):
    form_class = tier_forms.UpdateForm
    form_id = "update_tier_form"
    modal_header = _("Update Tier")
    template_name = 'nuage/applications/tiers/update.html'
    success_url = 'horizon:project:applications:detail'
    submit_url = 'horizon:project:applications:tiers:update'
    page_title = _("Update Tier")
    submit_label = _("Update Tier")

    def get_success_url(self):
        return reverse(self.success_url, args=(
            self._get_object()['associatedappid'],))

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["tier_id"] = self.kwargs['tier_id']
        tier = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(tier['id'],))
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        tier_id = self.kwargs['tier_id']
        try:
            return neutron.tier_get(self.request, tier_id)
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve tier details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        tier = self._get_object()
        initial = {'tier_id': tier['id'],
                   'type': tier['type'],
                   'description': tier.get('description'),
                   'name': tier.get('name')}
        return initial
