from datetime import datetime
from lib2to3.fixes.fix_input import context

import pandas as pd
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, FormView, UpdateView, DeleteView
from nadejda_94_django.glasses.models import Glasses
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.forms import RecordCreateForm, ReportsCreateForm, RecordUpdateForm, CreatePartnerForm
from nadejda_94_django.records.helpers import get_close_balance, get_order, errors_test, create_firm_report
from nadejda_94_django.records.models import Record, Partner

MAX_ROWS = 200
SUPPLIER = 1

class OrderCreateView(PermissionRequiredMixin, CreateView):
    context_object_name = 'form'

    def get(self, request,  *args, **kwargs):
        form = self.get_form()
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        if current_pk in (1, 2):
            firm_report = []
        else:
            firm_report = create_firm_report(current_partner)

        return self.render_to_response({
                'form': form,
                'partner': current_partner,
                'report': firm_report,
            })

class RecordCreateView(OrderCreateView):
    model = Record
    template_name = 'records/create_record.html'
    form_class = RecordCreateForm
    permission_required = 'records.add_record'
    success_url = reverse_lazy('dashboard')

    def post(self, request, *args, **kwargs):
        form = RecordCreateForm(request.POST)
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        if form.is_valid():
            record = form.save(commit=False)

            if record.order_type == 'G':
                note = record.note
                return redirect('glass_create', current_pk, note)

            record.warehouse = users_dict[request.user.username]
            record.order = get_order(record.order_type)
            record.partner_id = current_pk

            if record.partner_id == SUPPLIER:
                record.amount = -abs(record.amount)
            record.save()

            current_partner.balance = get_close_balance(
                current_pk,
                record.order_type,
                record.amount
            )
            current_partner.save()

            return redirect(self.success_url)


class RecordUpdateView(PermissionRequiredMixin, UpdateView):
    model = Record
    template_name = 'records/update_record.html'
    form_class = RecordUpdateForm
    pk_url_kwarg = 'record_pk'
    success_url = reverse_lazy('dashboard')
    permission_required = 'records.change_record'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = {}

        form = RecordUpdateForm(instance=self.object)
        current_record = Record.objects.get(pk=self.kwargs['record_pk'])

        context['form'] = form
        context['current_record'] = current_record

        return context

    def post(self, request, *args, **kwargs):
        form = RecordUpdateForm(request.POST)
        self.object = self.get_object()
        partner_pk = self.object.partner_id
        order_type = self.object.order_type
        old_amount = self.object.amount

        if form.is_valid():
            new_amount = form.cleaned_data['amount']
            difference = new_amount - old_amount

            current_partner = Partner.objects.get(pk=partner_pk)
            current_partner.balance = get_close_balance(partner_pk, order_type, difference)
            current_partner.save()

            self.object.amount = new_amount
            self.object.save()

        return super().post(request, *args, **kwargs)


class RecordGlassDeleteView(PermissionRequiredMixin, TemplateView):
    model = Record
    template_name = 'glasses/delete_glass_record.html'
    success_url = reverse_lazy('dashboard')
    permission_required = 'records.change_record'
    login_url = 'login'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        record_pk = self.kwargs['record_pk']
        context['record_pk'] = record_pk
        context['orders'] = Glasses.objects.filter(record=record_pk).order_by('pk')

        return context

    def post(self, request, *args, **kwargs):
        record_pk = self.kwargs['record_pk']
        record = Record.objects.get(pk=record_pk)
        partner = Partner.objects.get(pk=record.partner_id)
        glass_orders = Glasses.objects.filter(record=record_pk)
        all_glass_price = glass_orders.aggregate(Sum('price'))['price__sum']

        partner.balance += all_glass_price
        partner.save()

        record.amount -= all_glass_price

        if record.order.startswith('C'):
            record.note = 'Изтрита поръчка'

        record.save()


        for order in glass_orders:
            order.delete()

        return redirect(self.success_url)


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

                if current_partner.id == 2:
                    all_firms_report = Partner.objects.all().order_by('balance')
                    context['report'] = all_firms_report

                    return render(request, 'records/firm_report.html', context)

                name_report = (f"Отчет за фирма {current_partner}"
                               f" с баланс: {balance if balance is not None else 0} лв")

                context['report'] = create_firm_report(current_partner)[:MAX_ROWS]

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
                name = f"Report - {datetime.today().now()}"

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


class PartnerCreateView(PermissionRequiredMixin, CreateView):
    model = Partner
    form_class = CreatePartnerForm
    template_name = 'records/partner_create.html'
    success_url = reverse_lazy('dashboard')
    permission_required = ('records.add_partner',)


class ErrorTestView(PermissionRequiredMixin, TemplateView):
    model = Record
    template_name = 'records/errors_test.html'
    permission_required = ('records.add_partner',)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['errors_test'] = errors_test()

        return context
