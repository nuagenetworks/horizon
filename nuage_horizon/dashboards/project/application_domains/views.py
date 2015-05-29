from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import forms
from horizon import exceptions
from horizon.utils import memoized

from nuage_horizon.dashboards.project.application_domains \
    import tables as app_domain_tables
from nuage_horizon.dashboards.project.applications \
    import tables as app_tables
from nuage_horizon.api import neutron
from . import forms as app_domain_forms
from nuage_horizon.dashboards.project.applications import views as app_views


class CreateView(forms.ModalFormView):
    form_class = app_domain_forms.CreateForm
    form_id = "create_app_domain_form"
    modal_header = _("Create Application Domain")
    template_name = 'project/application_domains/create.html'
    success_url = reverse_lazy("horizon:project:application_domains:index")
    page_title = _("Create Application Domain")
    submit_label = _("Create")
    submit_url = reverse_lazy("horizon:project:application_domains:create")


class UpdateView(forms.ModalFormView):
    form_class = app_domain_forms.UpdateForm
    form_id = "update_app_domain_form"
    modal_header = _("Update Application Domain")
    template_name = 'project/application_domains/update.html'
    success_url = reverse_lazy("horizon:project:application_domains:index")
    page_title = _("Update Application Domain")
    submit_label = _("Update")
    submit_url = "horizon:project:application_domains:update"

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.kwargs['app_domain_id'],)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def _get_object(self):
        app_domain_id = self.kwargs['app_domain_id']
        try:
            return neutron.application_domain_get(self.request, app_domain_id)
        except Exception:
            redirect = self.success_url
            msg = _('Unable to retrieve Application Domain details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        app_domain = self._get_object()
        initial = {'app_domain_id': app_domain['id'],
                   'name': app_domain['name'],
                   'description': app_domain.get('description')}
        return initial


class IndexView(tables.DataTableView):
    table_class = app_domain_tables.ApplicationDomainsTable
    template_name = 'nuage/application_domains/index.html'

    def get_data(self):
        try:
            app_domains = neutron.application_domain_list(self.request)
        except Exception:
            app_domains = []
            msg = _('Application Domain list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return app_domains


class DetailView(tables.DataTableView):
    table_class = app_tables.ApplicationsTable
    template_name = 'nuage/application_domains/detail.html'
    page_title = _("Application Domain Details: {{ app_domain.name }}")

    def get_data(self):
        try:
            app_domain_id = self.kwargs['app_domain_id']
            apps = neutron.application_list(self.request)
            apps = [app for app in apps
                    if app.get('associateddomainid') == app_domain_id]
        except Exception:
            apps = []
            msg = _('Application list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return apps

    @memoized.memoized_method
    def _get_data(self):
        try:
            id = self.kwargs['app_domain_id']
            app_domain = neutron.application_domain_get(self.request, id)
        except Exception:
            msg = _('Unable to retrieve details for Application Domain "%s".') \
                  % (id)
            failure_url = reverse('horizon:project:application_domains:index')
            exceptions.handle(self.request, msg,
                              redirect=failure_url)
        return app_domain

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        app_domain = self._get_data()
        context["app_domain"] = app_domain
        table = app_domain_tables.ApplicationDomainsTable(self.request)
        context["url"] = self.get_redirect_url()
        context["actions"] = table.render_row_actions(app_domain)
        return context

    @staticmethod
    def get_redirect_url():
        return reverse_lazy('horizon:project:application_domains:index')


class CreateApplicationView(app_views.CreateView):
    def get_success_url(self):
        return reverse(
            'horizon:project:application_domains:detail',
            args=(self.kwargs['app_domain_id'],))

    def get_submit_url(self):
        return reverse(
            'horizon:project:application_domains:createApplication',
            args=(self.kwargs['app_domain_id'],))

    success_url = get_success_url
    submit_url = get_submit_url

    def get_initial(self):
        return {'domain_id': self.kwargs['app_domain_id']}


class UpdateApplicationView(app_views.UpdateView):
    def get_success_url(self):
        return reverse(
            'horizon:project:application_domains:detail',
            args=(self.kwargs['app_domain_id'],))

    def get_submit_url(self):
        return reverse(
            'horizon:project:application_domains:updateApplication',
            args=(self.kwargs['app_domain_id'], self.kwargs['application_id']))

    success_url = get_success_url
    submit_url = get_submit_url

