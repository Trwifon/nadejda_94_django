from datetime import date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from nadejda_94_django.common.forms import PartnerForm, SearchForm
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.models import Record


class Dashboard(LoginRequiredMixin, TemplateView, FormView):
    template_name = 'common/dashboard.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = {}

        context['current_path'] = self.request.path

        create_form = PartnerForm
        context['create_form'] = create_form

        search_form = SearchForm()
        context['search_form'] = search_form

        day_report = (Record.objects.filter(created_at=date.today())
                      .filter(warehouse=users_dict[self.request.user.username])
                      .order_by('-id'))
        context['report'] = day_report

        total_sum = day_report.filter(order_type='C').aggregate(Sum('amount'))
        context['total_sum'] = total_sum['amount__sum']

        return context

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('partner')

        if 'create' in request.POST:
            return redirect('record_create', pk)

        if 'search' in request.POST:
            context = {}
            query = request.POST.get('search_field')

            if query:
                report = ((Record.objects
                          .filter(Q(order__icontains=query) | Q(note__icontains=query)))
                          .order_by('-pk'))

                context['report'] = report

            return render(request, 'records/show_report.html', context)
