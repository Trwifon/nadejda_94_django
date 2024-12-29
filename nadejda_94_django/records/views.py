from datetime import datetime
import pandas as pd
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, FormView, UpdateView
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.forms import RecordCreateForm, ReportsCreateForm, RecordUpdateForm
from nadejda_94_django.records.helpers import get_close_balance, get_order, update_order
from nadejda_94_django.records.models import Record, Partner

MAX_ROWS = 200


class RecordCreateView(PermissionRequiredMixin, CreateView):
    model = Record
    form_class = RecordCreateForm
    template_name = 'records/create_record.html'
    context_object_name = 'form'
    permission_required = 'records.add_record'

    def get(self, request,  *args, **kwargs):
        form = RecordCreateForm()
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        if current_pk == 1:
            firm_report = []
        else:
            firm_report = Record.objects.filter(partner=current_partner).order_by('-pk')

        return self.render_to_response({
                'form': form,
                'partner': current_partner,
                'report': firm_report,
            })

    def post(self, request, *args, **kwargs):
        form = RecordCreateForm(request.POST)
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)
        open_balance = current_partner.balance

        if current_pk == 1:
            firm_report = []
        else:
            firm_report = Record.objects.filter(partner=current_partner).order_by('-pk')


        if form.is_valid():
            record = form.save(commit=False)
            record.warehouse = users_dict[request.user.username]
            record.balance = get_close_balance(
                current_pk,
                record.order_type,
                open_balance,
                record.amount
                )
            record.order = get_order(record.order_type)
            record.partner_id = current_pk

            if record.partner_id == 1:
                record.amount = -abs(record.amount)

            if 'bal' in request.POST:
                context = {
                    'form': form,
                    'partner': current_partner,
                    'report': firm_report,
                    'close_balance': record.balance,
                    'order': record.order,
                }

                return render(request, 'records/create_record.html', context)


            elif 'save' in request.POST:
                update_order(record.order_type)

                current_partner.balance = record.balance
                current_partner.save()

                record.save()
                return redirect('dashboard')


class RecordUpdateView(PermissionRequiredMixin, UpdateView):
    model = Record
    template_name = 'records/update_record.html'
    form_class = RecordUpdateForm
    pk_url_kwarg = 'record_pk'
    success_url = reverse_lazy('dashboard')

    permission_required = 'records.change_record'
    login_url = 'login'


class ReportsCreateView(PermissionRequiredMixin, TemplateView, FormView):
    template_name = 'records/create_report.html'
    form_class = ReportsCreateForm
    permission_required = 'records.change_record'

    def post(self, request, *args, **kwargs):
        form = ReportsCreateForm(request.POST)

        if form.is_valid():
            current_report = form.cleaned_data['report_field']
            name_report = ''
            current_date = form.cleaned_data['date_field']
            current_warehouse = form.cleaned_data['warehouse']

            context = {
                'form': form,
                'name_report': name_report,
                'report': '',
            }

            if current_report == 'FR':
                current_partner = form.cleaned_data['firm_field']
                balance = current_partner.balance
                name_report = (f"Отчет за фирма {current_partner}"
                               f" с баланс: {balance if balance is not None else 0} лв")
                firm_report = Record.objects.filter(partner=current_partner).order_by('-pk')[:MAX_ROWS]

                context['report'] = firm_report

            elif current_report == 'DR':
                day_report = (Record.objects
                              .filter(created_at=current_date)
                              .exclude(warehouse='M')
                              .order_by('-pk'))

                if current_warehouse != 'M':
                    day_report = day_report.filter(warehouse=current_warehouse)

                turnover = day_report.filter(order_type='C').aggregate(total=Sum('amount'))
                name_report = (f"Отчет за {current_date} с дневен касов оборот "
                               f"{turnover['total'] if turnover['total'] is not None else 0} лв")

                context['report'] = day_report

            elif current_report == 'MR':
                month_report = (Record.objects
                                .filter(created_at__month=current_date.month)
                                .filter(created_at__year=current_date.year)
                                .exclude(warehouse='M')
                                .order_by('-pk'))

                if current_warehouse != 'M':
                    month_report = month_report.filter(warehouse=current_warehouse)

                turnover = month_report.filter(order_type='C').aggregate(total=Sum('amount'))
                name_report = (f"Отчет за месец {current_date.month} с касов оборот "
                               f"{turnover['total'] if turnover['total'] is not None else 0} лв")

                context['report'] = month_report

            context['name_report'] = name_report

            if 'display' in request.POST:
                return render(request, 'records/show_report.html', context)

            elif 'excel' in request.POST:
                result = []

                for record in context['report']:
                    result.append({
                        'id': record.id,
                        'Дата': record.created_at,
                        'Фирма': record.partner,
                        'Склад': record.get_warehouse_display(),
                        'Вид поръчка': record.get_order_type_display(),
                        'Сума': record.amount,
                        'Баланс': record.balance,
                        'Номер поръчка': record.order,
                        'Забележка': record.note,
                    })

                df = pd.DataFrame(list(result))
                name = f"Отчет - {datetime.today().date()}"

                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename={name}.xlsx'

                df.to_excel(response, index=False, engine='openpyxl')

                return response


class ReportShowView(TemplateView):
    template_name = 'records/show_report.html'


class CashShowView(UserPassesTestMixin, TemplateView):
    template_name = 'records/cash_report.html'
    login_url = '/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cash = Record.objects.filter(order_type='C').aggregate(total=Sum('amount'))
        context['cash'] = cash

        return context

    def test_func(self):
        return self.request.user.is_staff




