from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import tables
from horizon import forms
from horizon.utils import memoized

from nuage_horizon.api import neutron

from nuage_horizon.dashboards.project.applications \
    import tables as application_tables
from nuage_horizon.dashboards.project.applications.tiers \
    import tables as tier_tables
from nuage_horizon.dashboards.project.applications.flows \
    import tables as flow_tables
from nuage_horizon.dashboards.project.applications \
    import forms as application_forms


class IndexView(tables.DataTableView):
    table_class = application_tables.ApplicationsTable
    template_name = 'nuage/applications/index.html'

    def get_data(self):
        try:
            applications = neutron.application_list(self.request)
        except Exception:
            applications = []
            msg = _('Application list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return applications


class DetailView(tables.MultiTableView):
    table_classes = (tier_tables.TiersTable, flow_tables.FlowsTable)
    template_name = 'nuage/applications/detail.html'
    page_title = _("Application Details: {{ application.name }}")
    tiers = []

    @memoized.memoized_method
    def get_tiers_data(self):
        if self.tiers:
            return self.tiers
        try:
            app = self._get_application_data()
            tiers = neutron.tier_list(self.request, app_id=app.id)
        except Exception:
            tiers = []
            msg = _('Tier list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return tiers

    @memoized.memoized_method
    def get_flows_data(self):
        request = self.request
        try:
            app = self._get_application_data()
            flows = neutron.flow_list(request, app_id=app.id)
            tiers = self.get_tiers_data()
            key_tiers = dict([(tier['id'], tier) for tier in tiers])
            res = []
            for flow in flows:
                flow_dict = neutron.flow_get(request, flow['id']).to_dict()
                if flow_dict['origin_tier']:
                    flow_dict['origin_tier'] = key_tiers[
                        flow_dict['origin_tier']]
                if flow_dict['dest_tier']:
                    flow_dict['dest_tier'] = key_tiers[flow_dict['dest_tier']]
                flow = neutron.NuageFlow(flow_dict)
                res.append(flow)
        except Exception:
            res = []
            msg = _('Flow list can not be retrieved.')
            exceptions.handle(request, msg)
        return res

    @memoized.memoized_method
    def _get_application_data(self):
        try:
            app_id = self.kwargs['application_id']
            application = neutron.application_get(self.request, app_id)
        except Exception:
            msg = _('Application can not be retrieved.')
            exceptions.handle(self.request, msg)
        return application

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        application = self._get_application_data()
        context["application"] = application
        table = application_tables.ApplicationsTable(self.request, self.kwargs)
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(application)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:project:applications:index')


class CreateView(forms.ModalFormView):
    form_class = application_forms.CreateForm
    form_id = "create_application_form"
    modal_header = _("Create Application")
    template_name = 'nuage/applications/create.html'
    success_url = reverse_lazy("horizon:project:applications:index")
    page_title = _("Create Application")
    submit_label = _("Create Application")
    submit_url = reverse_lazy("horizon:project:applications:create")


class UpdateView(forms.ModalFormView):
    form_class = application_forms.UpdateForm
    form_id = "update_application_form"
    modal_header = _("Update Application")
    template_name = 'nuage/applications/update.html'
    success_url = reverse_lazy("horizon:project:applications:index")
    page_title = _("Update Application")
    submit_label = _("Update Application")
    submit_url = "horizon:project:applications:update"

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['submit_url'] = self.get_submit_url()
        return context

    def get_submit_url(self):
        args = (self.kwargs['application_id'],)
        return reverse(self.submit_url, args=args)

    def _get_object(self, *args, **kwargs):
        application_id = self.kwargs['application_id']
        try:
            return neutron.application_get(self.request, application_id)
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve application details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        application = self._get_object()
        initial = {'application_id': application['id'],
                   'domain_id': application['associateddomainid'],
                   'name': application['name']}
        return initial
