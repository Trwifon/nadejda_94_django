from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from nadejda_94_django.common.forms import PartnerForm
from nadejda_94_django.records.models import Partner


class Dashboard(LoginRequiredMixin, TemplateView, FormView):
    model = Partner
    form_class = PartnerForm
    template_name = 'common/dashboard.html'
    login_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('partner')

        return redirect('record_create', pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_path = self.request.path
        context['current_path'] = current_path

        return context




