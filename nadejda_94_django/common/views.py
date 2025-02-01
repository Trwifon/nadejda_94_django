from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from pandas.core.computation.align import reconstruct_object

from nadejda_94_django.common.forms import PartnerForm
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.models import Partner, Record


class Dashboard(LoginRequiredMixin, TemplateView, FormView):
    model = Partner
    form_class = PartnerForm
    template_name = 'common/dashboard.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['current_path'] = self.request.path

        day_report = (Record.objects.filter(created_at=date.today())
                      .filter(warehouse=users_dict[self.request.user.username])
                      .order_by('-id'))

        context['report'] = day_report

        total_sum = day_report.filter(order_type='C').aggregate(Sum('amount'))
        context['total_sum'] = total_sum['amount__sum']

        return context

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('partner')

        if 'choice' in request.POST:
            return redirect('record_create', pk)
