from datetime import datetime, timedelta
import pandas as pd
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Sum, F, ExpressionWrapper, FloatField, Case, When
from django.http import request
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, TemplateView, FormView, CreateView
from nadejda_94_django.glasses.forms import GlassCreateForm, GlassUpdateForm, GlassProductionForm, PGlassCreateForm
from nadejda_94_django.glasses.helpers import calculate_price, get_glass_kind, calculate_area, calculate_glass_data
from nadejda_94_django.glasses.models import Glasses, Partner, Record
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.helpers import get_order, get_close_balance
from nadejda_94_django.records.views import OrderCreateView

ALL_ORDERS = []

class GlassCreateView(OrderCreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    ALL_ORDERS = []

    def get_context_data(self, **kwargs):
        form = GlassCreateForm(self.request.POST)
        note = self.kwargs.get('note')
        current_pk = self.kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        context = {
            'form': form,
            'note': note,
            'partner': current_partner,
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return render(request, 'glasses/create_glass.html', context)

    def post(self, request, *args, **kwargs):
        form = GlassCreateForm(request.POST)
        current_pk = self.kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        context = self.get_context_data()

        if form.is_valid():
            current_order = form.cleaned_data

            if 'order' in request.POST:
                ALL_ORDERS.append(current_order)
                context['orders'] = ALL_ORDERS
                context['glass_data'] = calculate_glass_data(ALL_ORDERS)

                return render(request, 'glasses/create_glass.html', context)

            if 'save' in request.POST:
                order = get_order('G')
                current_amount = sum(item['price'] for item in ALL_ORDERS)

                record = Record(
                    warehouse = users_dict[request.user.username],
                    order_type = 'G',
                    amount = current_amount,
                    order = order,
                    note = context['note'],
                    partner = current_partner
                )
                current_partner.balance = get_close_balance(current_pk, 'G', current_amount)
                current_partner.save()
                record.save()

                for element in ALL_ORDERS:
                    element['record'] = record

                element_instances = [Glasses(**element) for element in ALL_ORDERS]
                Glasses.objects.bulk_create(element_instances)
                glass_pk = Glasses.objects.filter(record=record).first().pk

                ALL_ORDERS.clear()

                return redirect('glass_update', record_pk=record.pk, pk=glass_pk, old_total=int(current_amount))

            if 'cancel' in request.POST:
                ALL_ORDERS.clear()

                return redirect('dashboard')


class PGlassCreateView(PermissionRequiredMixin, CreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    success_url = reverse_lazy('dashboard')
    form_class = PGlassCreateForm
    ALL_ORDERS = []

    def get(self, request, *args, **kwargs):
        record_pk = self.kwargs.get('record_pk')
        glass = Glasses.objects.filter(record_id=record_pk).first()

        if glass:
            return redirect('glass_details', record_pk=record_pk)

        return render(request, 'glasses/create_glass.html', self.get_context_data())

    def get_context_data(self, **kwargs):
        form = PGlassCreateForm(self.request.POST)
        note = self.kwargs.get('note')
        record_pk = self.kwargs.get('record_pk')
        record = Record.objects.get(pk=record_pk)
        partner = record.partner

        context = {
            'form': form,
            'note': note,
            'record': record,
            'partner': partner,
        }

        return context

    def post(self, request, *args, **kwargs):
        form = GlassCreateForm(request.POST)

        context = self.get_context_data()

        if form.is_valid():
            current_order = form.cleaned_data

            if 'order' in request.POST:
                ALL_ORDERS.append(current_order)
                context['orders'] = ALL_ORDERS
                context['glass_data'] = calculate_glass_data(ALL_ORDERS)

                return render(request, 'glasses/create_glass.html', context)

            if 'save' in request.POST:
                record_pk = self.kwargs.get('record_pk')
                record = Record.objects.get(pk=record_pk)
                # current_amount = sum(item['price'] for item in ALL_ORDERS)

                for element in ALL_ORDERS:
                    element['record'] = record

                element_instances = [Glasses(**element) for element in ALL_ORDERS]
                Glasses.objects.bulk_create(element_instances)
                ALL_ORDERS.clear()

                glass_pk = Glasses.objects.filter(record=record).first().pk

                return redirect('glass_update', record_pk=record.pk, pk=glass_pk)

            if 'cancel' in request.POST:
                ALL_ORDERS.clear()

                return redirect('dashboard')


class GlassListView(ListView):
    model = Glasses
    template_name = 'glasses/details_glass.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}

        record_pk = self.kwargs['record_pk']
        context['record_pk'] = record_pk

        orders = Glasses.objects.filter(record=record_pk).order_by('pk')
        context['orders'] = orders

        old_total_price = orders.aggregate(amount=Sum('price'))['amount']
        context['old_total'] = int(old_total_price)

        return context


class GlassUpdateView(TemplateView):
    template_name = 'glasses/update_glass.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Glasses.objects.filter(record=self.kwargs.get('record_pk')).order_by('pk')
        context['orders'] = orders

        row_glass_data = orders.annotate(
            area = ExpressionWrapper(F('width') * F('height'), output_field=FloatField()),
            row_area = Case(
                When(area__gte=300000, then=(F('area') * F('number'))),
                When(area__lt=300000, then=(300000 * F('number'))),
                output_field=FloatField()
            ),
            row_price = ExpressionWrapper(F('unit_price') * F('row_area'), output_field=FloatField())
        )

        glass_data = row_glass_data.aggregate(
            total_number = Sum('number'),
            total_area = Sum('row_area'),
            total_price = Sum('row_price'),
        )
        glass_data['total_area'] /= 1000000
        glass_data['total_price'] /= 1000000

        context['glass_data'] = glass_data

        current_index = kwargs.get('pk')
        current_order = [el for el in orders if el.pk == current_index]

        form = GlassUpdateForm(instance=current_order[0])
        context['form'] = form

        order_list = [order.pk for order in orders]

        if current_index > order_list[0]:
            context['prev_order'] = current_index - 1
        if current_index < order_list[-1]:
            context['next_order'] = current_index + 1

        return context

    def post(self, request, record_pk, pk, **kwargs):
        order = get_object_or_404(Glasses, pk=pk)
        old_total_price = kwargs.get('old_total')
        form = GlassUpdateForm(request.POST, instance=order)

        if form.is_valid():
            instance = form.save(commit=False)

            area = calculate_area(instance.width, instance.height, instance.number)
            instance.price = calculate_price(
                area,
                float(instance.unit_price),
            )

            instance.save()

            if 'Next' in request.POST:
                return redirect('glass_update', record_pk=record_pk, pk=pk+1, old_total=old_total_price)
            elif 'Previous' in request.POST:
                return redirect('glass_update', record_pk=record_pk, pk=pk-1, old_total=old_total_price)

            current_record = Record.objects.get(pk=record_pk)
            partner = Partner.objects.get(pk=current_record.partner.pk)
            old_total_price = kwargs.get('old_total')
            new_total_price = Glasses.objects.filter(record=current_record).aggregate(amount=Sum('price'))
            difference = old_total_price - new_total_price['amount']

            if current_record.order.startswith('C'):
                current_record.amount = new_total_price['amount']
                current_record.save()

                partner.balance += difference
                partner.save()

                return redirect('dashboard')

            else:
                context = {
                    'record': current_record,
                    'partner': partner,
                    'difference': difference,
                    'message': f"Искате ли да добавите сумата {difference} към поръчка {current_record.order}?"
                }
                return render(request, 'glasses/record_price_increase.html', context)


class RecordsPriceIncreaseView(TemplateView):
    template_name = 'glasses/record_price_increase.html'

    def get(self, **kwargs):
        price = kwargs['price']

        return render(request, self.template_name, {'price': price})


class GlassDeleteView(DeleteView):
    pass


class GlassProductionView(PermissionRequiredMixin, FormView):
    template_name = 'glasses/glass_production.html'
    form_class = GlassProductionForm
    success_url = 'glasses/glass_production.html'
    permission_required = 'glasses.add_glasses'

    def get_context_data(self, **kwargs):
        context = {}

        orders = Glasses.objects.filter(prepared_for_working=False).order_by('record__order', 'pk')
        labels = sorted(set([label.record.order for label in orders]))
        choices = [(el, el) for el in labels]

        form = GlassProductionForm()
        form.fields['order_choice'].choices = choices
        context['form'] = form

        for order in orders:
            order.kind = get_glass_kind(order)

        context['orders'] = orders

        production_orders = Glasses.objects.filter(prepared_for_working=True).filter(sent_for_working = None).order_by('pk')
        production_labels = sorted(set([label.record.order for label in production_orders]))
        production_choices = [(el, el) for el in production_labels]

        production_form = GlassProductionForm()
        production_form.fields['order_choice'].choices = production_choices
        context['production_form'] = production_form

        for order in production_orders:
            order.kind = get_glass_kind(order)

        context['production_orders'] = production_orders

        return context

    def post(self, request, *args, **kwargs):
        if 'ok' in request.POST:
            glasses = (Glasses.objects
                       .filter(prepared_for_working=True)
                       .filter(sent_for_working=None)
                       .order_by('pk'))
            sent_time = ''

            for glass in glasses:
                glass.sent_for_working = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                glass.save()
                sent_time = glass.sent_for_working

            return redirect('glass_excel', sent_time=sent_time)

        if 'glass_submit' or 'production_glass_submit' in request.POST:
            choice = request.POST['order_choice']
            orders = Glasses.objects.filter(record__order=choice).order_by('pk')
            for order in orders:
                order.prepared_for_working = True if 'glass_submit' in request.POST else False
                order.save()

            return redirect('glass_production')


class ExcelGlassView(TemplateView):
    template_name = 'glasses/excel_glass.html'
    success_url = reverse_lazy('/glasses/dashboard.html')
    form_class = GlassProductionForm

    def post(self, request, *args, **kwargs):
        if 'dashboard' in request.POST:
            return redirect('dashboard')

        sent_time_str = kwargs['sent_time']
        sent_time = datetime.strptime(sent_time_str, '%Y-%m-%d %H:%M:%S')

        glasses = Glasses.objects.filter(sent_for_working__in=[
            sent_time - timedelta(seconds=2),
            sent_time - timedelta(seconds=1),
            sent_time,
            sent_time + timedelta(seconds=1),
            sent_time + timedelta(seconds=2),
        ]).order_by('pk')

        number_of_glasses = glasses.aggregate(sum=Sum('number'))
        total_area = 0.0

        glass_order = []
        row = 0
        old_order = ''

        for glass in glasses:
            current_order = glass.record.order
            quantity = glasses.filter(record__order=current_order).aggregate(sum=Sum('number'))
            if current_order == old_order:
                row += 1
            else:
                row = 1

            old_order = current_order

            if glass.record.note == 'None' or not glass.record.note:
                first_column = f"{glass.record.partner.name} / {quantity['sum']}"
            else:
                if glass.record.partner.name == 'Клиент':
                    first_column = f"{glass.record.note} / {quantity['sum']}"
                else:
                    first_column = f"{glass.record.partner.name} / {glass.record.note} / {quantity['sum']}"

            glass_order.append([
                first_column,
                f"{current_order} {row}",
                glass.width,
                glass.height,
                'R',
                glass.number,
                glass.number,
                get_glass_kind(glass),
            ])

            total_area += calculate_area(glass.width, glass.height, glass.number)

        glass_order[0].extend([
            'Брой:',
            number_of_glasses['sum'],
            'Площ:',
            total_area,
            'кв.м'
        ])

        df = pd.DataFrame(glass_order)
        str_sent_time = str(sent_time).replace(':', '_')
        name = f"d:/paketi/Линия {str_sent_time}.xlsx"

        df.to_excel(name, index=False, header=False)

        return redirect('dashboard')







