from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import reverse

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon.utils import memoized
from horizon import views

from nuage_horizon.dashboards.project.application_services \
    import tables as app_service_tables
from nuage_horizon.dashboards.project.application_services \
    import forms as app_service_forms
from nuage_horizon.api import neutron


class IndexView(tables.DataTableView):
    table_class = app_service_tables.ApplicationServicesTable
    template_name = 'nuage/application_services/index.html'

    def get_data(self):
        try:
            app_services = neutron.application_service_list(self.request)
        except Exception:
            app_services = []
            msg = _('Application Service list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return app_services


class CreateView(forms.ModalFormView):
    form_class = app_service_forms.CreateForm
    form_id = "create_app_service_form"
    modal_header = _("Create Application Service")
    template_name = 'nuage/application_services/create.html'
    success_url = reverse_lazy('horizon:project:application_services:index')
    failure_url = reverse_lazy('horizon:project:application_services:index')
    submit_url = reverse_lazy('horizon:project:application_services:create')
    page_title = _("Create Application Service")
    submit_label = _("Create")


class DetailView(views.HorizonTemplateView):
    template_name = 'project/application_services/detail.html'
    page_title = _("Service Details")

    @memoized.memoized_method
    def _get_data(self):
        try:
            app_service = neutron.application_service_get(
                self.request, self.kwargs['application_service_id'])
        except Exception:
            redirect = reverse('horizon:project:application_services:index')
            msg = _('Unable to retrieve details for Aoplication Service '
                    '"%s".') % (self.kwargs['application_service_id'])
            exceptions.handle(self.request, msg, redirect=redirect)
        return app_service

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        app_service = self._get_data()
        context['app_service'] = app_service
        table = app_service_tables.ApplicationServicesTable(self.request)
        context["actions"] = table.render_row_actions(app_service)
        return context


class UpdateView(forms.ModalFormView):
    form_class = app_service_forms.UpdateForm
    form_id = "update_app_service_form"
    modal_header = _("Update Application Service")
    template_name = 'project/application_services/update.html'
    success_url = reverse_lazy("horizon:project:application_services:index")
    page_title = _("Update Application Service")
    submit_label = _("Update")
    submit_url = "horizon:project:application_services:update"

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.kwargs['application_service_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def _get_object(self):
        app_service_id = self.kwargs['application_service_id']
        try:
            return neutron.application_service_get(self.request,
                                                   app_service_id)
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve Application Service details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        app_service = self._get_object()
        initial = {'name': app_service['name'],
                   'application_service_id': app_service['id'],
                   'description': app_service.get('description')}
        return initial
