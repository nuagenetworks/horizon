from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import forms
from horizon import views
from horizon.utils import memoized

from nuage_horizon.api import neutron

from nuage_horizon.dashboards.project.applications.flows \
    import forms as flow_forms
from nuage_horizon.dashboards.project.applications.flows \
    import tables as flow_tables


class CreateView(forms.ModalFormView):
    form_class = flow_forms.CreateForm
    form_id = "create_flow_form"
    modal_header = _("Create Flow")
    template_name = 'nuage/applications/flows/create.html'
    success_url = 'horizon:project:applications:detail'
    failure_url = 'horizon:project:applications:detail'
    submit_url = 'horizon:project:applications:createflow'
    page_title = _("Create Flow")
    submit_label = _("Create Flow")

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


class DetailView(views.HorizonTemplateView):
    template_name = 'nuage/applications/flows/detail.html'
    page_title = _("Flow Details")

    @memoized.memoized_method
    def _get_data(self):
        try:
            flow = neutron.flow_get(self.request,
                                    self.kwargs['flow_id'])
        except Exception:
            redirect = reverse('horizon:project:applications:index')
            msg = (_('Unable to retrieve details for flow "%s".')
                   % self.kwargs['flow_id'])
            exceptions.handle(self.request, msg, redirect=redirect)
        return flow

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        flow = self._get_data()
        context['flow'] = flow
        table = flow_tables.FlowsTable(self.request)
        args = (flow.associatedappid,)
        context["url"] = reverse('horizon:project:applications:detail',
                                 args=args)
        context["actions"] = table.render_row_actions(flow)
        return context


class UpdateView(forms.ModalFormView):
    form_class = flow_forms.UpdateForm
    form_id = "update_flow_form"
    modal_header = _("Update Flow")
    template_name = 'nuage/applications/flows/update.html'
    success_url = 'horizon:project:applications:detail'
    submit_url = 'horizon:project:applications:flows:update'
    page_title = _("Update Flow")
    submit_label = _("Update Flow")

    def get_success_url(self):
        return reverse(self.success_url, args=(
            self._get_object()['application_id'],))

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["flow_id"] = self.kwargs['flow_id']
        flow = self._get_object()
        context['submit_url'] = reverse(self.submit_url,
                                        args=(flow['id'],))
        return context

    @memoized.memoized_method
    def _get_object(self, *args, **kwargs):
        flow_id = self.kwargs['flow_id']
        try:
            return neutron.flow_get(self.request, flow_id)
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve flow details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        flow = self._get_object()
        initial = {'flow_id': flow['id'],
                   'description': flow.get('description'),
                   'name': flow.get('name')}
        return initial
