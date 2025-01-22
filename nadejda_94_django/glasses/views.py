from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, View, TemplateView
from nadejda_94_django.glasses.forms import GlassCreateForm, GlassUpdateForm
from nadejda_94_django.glasses.helpers import calculate_price
from nadejda_94_django.glasses.models import Glasses, Partner, Record
from nadejda_94_django.records.choices import users_dict
from nadejda_94_django.records.helpers import get_order, get_close_balance
from nadejda_94_django.records.views import OrderCreateView

ALL_ORDERS = []


class GlassCreateView(OrderCreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    success_url = reverse_lazy('dashboard')
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
            current_order['price'] = calculate_price(
                current_order['width'],
                current_order['height'],
                float(current_order['unit_price']),
                current_order['number'],
            )

            if 'order' in request.POST:
                ALL_ORDERS.append(current_order)

                context['orders'] = ALL_ORDERS

                return render(request, 'glasses/create_glass.html', context)

            if 'save' in request.POST:
                order = get_order('G')

                current_amount = sum(item['price'] for item in ALL_ORDERS)

                record = Record(
                    warehouse = users_dict[request.user.username],
                    order_type = 'G',
                    amount = current_amount,
                    balance = get_close_balance(current_pk, 'G', current_amount),
                    order = order,
                    note = context['note'],
                    partner = current_partner
                )
                current_partner.balance = record.balance
                current_partner.save()
                record.save()

                for element in ALL_ORDERS:
                    element['order'] = record
                    element['partner'] = current_partner

                element_instances = [Glasses(**element) for element in ALL_ORDERS]
                Glasses.objects.bulk_create(element_instances)

                ALL_ORDERS.clear()

                return render(request, 'common/dashboard.html')


class GlassListView(ListView):
    model = Glasses
    template_name = 'glasses/details_glass.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {}
        record_pk = self.kwargs.get('record_pk')
        context['record_pk'] = record_pk

        orders = Glasses.objects.filter(order=record_pk).order_by('pk')
        context['orders'] = orders

        glass_order = orders.first()

        context['partner'] = glass_order.partner.name
        context['glass_order'] = glass_order.order.order
        context['pk'] = glass_order.id

        return context


class GlassUpdateView(TemplateView):
    template_name = 'glasses/update_glass.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Glasses.objects.filter(order=self.kwargs.get('record_pk')).order_by('pk')
        context['orders'] = orders
        form = GlassUpdateForm(instance=orders[0])
        context['form'] = form

        order_list = [order.pk for order in orders]

        current_index = order_list[0]

        if current_index > order_list[0]:
            context['prev_order'] = current_index - 1
        if current_index < order_list[-1]:
            context['next_order'] = current_index + 1

        return context

    def post(self, request, record_pk, pk, *args, **kwargs):
        order = get_object_or_404(Glasses, pk=pk)
        form = GlassUpdateForm(request.POST, instance=order)
        record_pk = 24527
        print(request)
        print(record_pk)
        if form.is_valid():
            form.save()
            return redirect('glass_update', record_pk=record_pk, pk=pk)

        return render(request, 'common/dashboard.html')






class GlassDeleteView(DeleteView):
    pass