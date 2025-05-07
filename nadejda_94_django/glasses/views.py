import os
from datetime import datetime, timedelta
import pandas as pd
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Sum
from django.http import HttpResponseNotFound, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, TemplateView, FormView, CreateView
from nadejda_94_django.glasses.forms import GlassCreateForm, GlassUpdateForm, GlassProductionForm, PGlassCreateForm
from nadejda_94_django.glasses.helpers import calculate_price, get_glass_kind, calculate_area, calculate_glass_data, \
    format_excel, excel_glass_view
from nadejda_94_django.glasses.models import Glasses, Partner, Record
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.helpers import get_order, get_close_balance
from nadejda_94_django.records.views import OrderCreateView

ALL_ORDERS_TRIFON = []
ALL_ORDERS_TSONKA = []
ALL_ORDERS_NADYA = []
ALL_ORDERS = []

class GlassCreateView(OrderCreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    ALL_ORDERS_TRIFON = []
    ALL_ORDERS_TSONKA = []
    ALL_ORDERS_NADYA = []

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
            current_order['supplement'] = 0

            if request.user.username == 'Tsonka':
                if 'order' in request.POST:

                    ALL_ORDERS_TSONKA.append(current_order)
                    context['orders'] = ALL_ORDERS_TSONKA
                    context['glass_data'] = calculate_glass_data(ALL_ORDERS_TSONKA)

                    return render(request, 'glasses/create_glass.html', context)

                if 'save' in request.POST:
                    order = get_order('G')
                    current_amount = sum(item['price'] for item in ALL_ORDERS_TSONKA)

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

                    for element in ALL_ORDERS_TSONKA:
                        element['record'] = record

                    element_instances = [Glasses(**element) for element in ALL_ORDERS_TSONKA]
                    Glasses.objects.bulk_create(element_instances)
                    glass_pk = Glasses.objects.filter(record=record).first().pk

                    ALL_ORDERS_TSONKA.clear()

                    return redirect('glass_update', record_pk=record.pk, pk=glass_pk, old_total=int(current_amount))

                if 'cancel' in request.POST:
                    ALL_ORDERS_TSONKA.clear()

                    return redirect('dashboard')

            elif request.user.username == 'Nadya':
                if 'order' in request.POST:
                    ALL_ORDERS_NADYA.append(current_order)
                    context['orders'] = ALL_ORDERS_NADYA
                    context['glass_data'] = calculate_glass_data(ALL_ORDERS_NADYA)

                    return render(request, 'glasses/create_glass.html', context)

                if 'save' in request.POST:
                    order = get_order('G')
                    current_amount = sum(item['price'] for item in ALL_ORDERS_NADYA)

                    record = Record(
                        warehouse=users_dict[request.user.username],
                        order_type='G',
                        amount=current_amount,
                        order=order,
                        note=context['note'],
                        partner=current_partner
                    )
                    current_partner.balance = get_close_balance(current_pk, 'G', current_amount)
                    current_partner.save()
                    record.save()

                    for element in ALL_ORDERS_NADYA:
                        element['record'] = record

                    element_instances = [Glasses(**element) for element in ALL_ORDERS_NADYA]
                    Glasses.objects.bulk_create(element_instances)
                    glass_pk = Glasses.objects.filter(record=record).first().pk

                    ALL_ORDERS_NADYA.clear()

                    return redirect('glass_update', record_pk=record.pk, pk=glass_pk, old_total=int(current_amount))

                if 'cancel' in request.POST:
                    ALL_ORDERS_NADYA.clear()

                    return redirect('dashboard')


class PGlassCreateView(PermissionRequiredMixin, CreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    success_url = reverse_lazy('dashboard')
    form_class = PGlassCreateForm
    ALL_ORDERS_TRIFON = []
    ALL_ORDERS_TSONKA = []
    ALL_ORDERS_NADYA = []

    def get(self, request, *args, **kwargs):
        record_pk = self.kwargs.get('record_pk')
        orders = Glasses.objects.filter(record_id=record_pk)

        if orders:
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
            current_order['supplement'] = 0

            if request.user.username == 'Tsonka':
                if 'order' in request.POST:
                    ALL_ORDERS_TSONKA.append(current_order)
                    context['orders'] = ALL_ORDERS_TSONKA
                    context['glass_data'] = calculate_glass_data(ALL_ORDERS_TSONKA)

                    return render(request, 'glasses/create_glass.html', context)

                if 'save' in request.POST:
                    record_pk = self.kwargs.get('record_pk')
                    current_record = Record.objects.get(pk=record_pk)
                    all_glass_price = sum(item['price'] for item in ALL_ORDERS_TSONKA)
                    difference = -int(all_glass_price)

                    for order in ALL_ORDERS_TSONKA:
                        order['record'] = current_record

                    order_instances = [Glasses(**order) for order in ALL_ORDERS_TSONKA]
                    Glasses.objects.bulk_create(order_instances)
                    ALL_ORDERS_TSONKA.clear()

                    return redirect('record_price_increase', record_pk=current_record.pk, diff=difference, to_update=True)

                if 'cancel' in request.POST:
                    ALL_ORDERS_TSONKA.clear()

                    return redirect('dashboard')
            if request.user.username == 'Nadya':
                if 'order' in request.POST:
                    ALL_ORDERS_NADYA.append(current_order)
                    context['orders'] = ALL_ORDERS_NADYA
                    context['glass_data'] = calculate_glass_data(ALL_ORDERS_NADYA)

                    return render(request, 'glasses/create_glass.html', context)

                if 'save' in request.POST:
                    record_pk = self.kwargs.get('record_pk')
                    current_record = Record.objects.get(pk=record_pk)
                    all_glass_price = sum(item['price'] for item in ALL_ORDERS_NADYA)
                    difference = -int(all_glass_price)

                    for order in ALL_ORDERS_NADYA:
                        order['record'] = current_record

                    order_instances = [Glasses(**order) for order in ALL_ORDERS_NADYA]
                    Glasses.objects.bulk_create(order_instances)
                    ALL_ORDERS_NADYA.clear()

                    return redirect('record_price_increase', record_pk=current_record.pk, diff=difference,
                                    to_update=True)

                if 'cancel' in request.POST:
                    ALL_ORDERS_NADYA.clear()

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
        ALL_ORDERS = list(orders.values())
        glass_data = calculate_glass_data(ALL_ORDERS)
        context['glass_data'] = glass_data

        old_total_price = Record.objects.get(pk=record_pk).amount
        context['old_total'] = int(old_total_price)

        return context


class GlassUpdateView(TemplateView):
    template_name = 'glasses/update_glass.html'
    permission_required = 'glasses.add_glasses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Glasses.objects.filter(record=self.kwargs.get('record_pk')).order_by('pk')

        partner = orders.first().record.partner
        context['partner'] = partner

        order = orders.first()
        context['order'] = order

        excel_view = excel_glass_view(orders)
        context['orders'] = excel_view['glass_order_with_additional_fields']

        ALL_ORDERS = list(orders.values())
        glass_data = calculate_glass_data(ALL_ORDERS)
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
        form = GlassUpdateForm(request.POST, instance=order)
        price_before_edit = kwargs.get('old_total')

        if form.is_valid():
            current_record = Record.objects.get(pk=record_pk)
            old_total_price = Glasses.objects.filter(record=current_record).aggregate(amount=Sum('price'))

            instance = form.save(commit=False)
            area = calculate_area(instance.width, instance.height, instance.number)
            supplement = instance.supplement if instance.supplement else 0
            instance.price = calculate_price(
                area,
                float(instance.unit_price),
                supplement
            )
            instance.save()

            new_total_price = Glasses.objects.filter(record=current_record).aggregate(amount=Sum('price'))
            difference = old_total_price['amount'] - new_total_price['amount']

            current_record.amount -= difference
            current_record.save()

            partner = Partner.objects.get(pk=current_record.partner.pk)
            partner.balance += difference
            partner.save()

            if 'Next' in request.POST:
                return redirect('glass_update', record_pk=record_pk, pk=pk+1, old_total=price_before_edit)

            if 'Previous' in request.POST:
                return redirect('glass_update', record_pk=record_pk, pk=pk-1, old_total=price_before_edit)

            if current_record.order.startswith('C'):
                return redirect('dashboard')

            else:
                total_difference = int(price_before_edit - current_record.amount)

                if total_difference != 0:
                    return redirect( 'record_price_increase', record_pk=record_pk, diff=total_difference, to_update=False)

                return redirect('dashboard')

class RecordPriceIncreaseView(TemplateView):
    template_name = 'glasses/record_price_increase.html'
    permission_required = 'glasses.add_glasses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_record = Record.objects.get(pk=context['record_pk'])
        context['record'] = current_record

        return context

    def post(self, request, **kwargs):
        current_record = Record.objects.get(pk=kwargs['record_pk'])
        to_update = kwargs.get('to_update')
        difference = int(kwargs.get('diff'))

        if to_update == 'True':
            if 'ok' in request.POST:
                current_record.amount -= difference
                current_record.save()

                current_record.partner.balance += difference
                current_record.partner.save()

            glass_pk = Glasses.objects.filter(record_id=current_record.pk).first().pk
            old_total_price = current_record.amount

            return redirect('glass_update', record_pk=current_record.pk, pk=glass_pk, old_total=int(old_total_price))

        else:
            if 'cancel' in request.POST:
                current_record.amount += difference
                current_record.save()

                current_record.partner.balance -= difference
                current_record.partner.save()

        return redirect('dashboard')


class GlassDeleteView(DeleteView):
    def post(self, request, *args, **kwargs):
        print(request.POST)
        print(kwargs)


class GlassProductionView(PermissionRequiredMixin, FormView):
    template_name = 'glasses/glass_production.html'
    form_class = GlassProductionForm
    success_url = 'glasses/glass_production.html'
    permission_required = 'glasses.add_glasses'

    def get_context_data(self, **kwargs):
        context = {}

        orders = (Glasses.objects
                  .filter(prepared_for_working=False)
                  .filter(number__gt=0)
                  .order_by('record__order', 'pk'))
        labels = sorted(set([label.record.order for label in orders]))
        choices = [(el, el) for el in labels]

        form = GlassProductionForm()
        form.fields['order_choice'].choices = choices
        context['form'] = form

        for order in orders:
            order.kind = get_glass_kind(order)

        context['orders'] = orders

        production_orders = (Glasses.objects
                             .filter(prepared_for_working=True)
                             .filter(sent_for_working = None)
                             .filter(number__gt=0)
                             .order_by('pk'))
        total_number = production_orders.aggregate(numbers=Sum('number'))['numbers']
        context['total_number'] = total_number

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
        glasses_to_produce = (Glasses.objects
                   .filter(prepared_for_working=True)
                   .filter(sent_for_working=None)
                   .filter(number__gt=0)
                   .order_by('pk'))

        if 'ok' in request.POST:
            sent_time = ''

            for glass in glasses_to_produce:
                glass.sent_for_working = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                glass.save()
                sent_time = glass.sent_for_working

            return redirect('glass_excel', sent_time=sent_time)

        choice = request.POST['order_choice']
        orders = Glasses.objects.filter(record__order=choice).order_by('pk')
        for order in orders:
            order.prepared_for_working = True if 'glass_submit' in request.POST else False
            order.save()

        return redirect('glass_production')


class ExcelGlassView(TemplateView):
    template_name = 'glasses/excel_glass.html'
    success_url = reverse_lazy('glasses_excel')
    form_class = GlassProductionForm

    def post(self, request, *args, **kwargs):
        sent_time_str = kwargs['sent_time']
        sent_time = datetime.strptime(sent_time_str, '%Y-%m-%d %H:%M:%S')
        str_sent_time = str(sent_time).replace(':', '_')
        name = f"Glass {str_sent_time}.xlsx"
        file_path = os.path.join('d:\paketi', name)

        if 'cancel' in request.POST:
            return redirect('dashboard')

        glasses = Glasses.objects.filter(sent_for_working__in=[
            sent_time - timedelta(seconds=3),
            sent_time - timedelta(seconds=2),
            sent_time - timedelta(seconds=1),
            sent_time,
            sent_time + timedelta(seconds=1),
            sent_time + timedelta(seconds=2),
            sent_time + timedelta(seconds=3),
        ]).order_by('pk')

        excel_view = excel_glass_view(glasses)

        df_glass = pd.DataFrame(excel_view['glass_order_list'])
        df_dist = pd.DataFrame(excel_view['dist_order_list'])

        for filename in os.listdir('d:\paketi'):
            file_path_to_remove = os.path.join('d:\paketi', filename)

            if os.path.isfile(file_path_to_remove):
                os.remove(file_path_to_remove)

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_glass.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
            df_dist.to_excel(writer, index=False, header=False, sheet_name='Dist')

        format_excel(file_path)

        if not os.path.exists(file_path):
            return HttpResponseNotFound('File not found.')

        response = FileResponse(open(file_path, 'rb'),
                                content_type='application/vnd'
                                             '.openxmlformats-officedocument'
                                             '.spreadsheetml'
                                             '.sheet')
        response['Content-Disposition'] = (f'attachment; '
                                           f'filename="{os.path.basename(file_path)}"')

        return response



