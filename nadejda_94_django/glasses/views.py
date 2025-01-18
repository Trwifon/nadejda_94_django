from django.contrib.messages import success
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from nadejda_94_django.glasses.forms import GlassCreateForm
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
    form_class = GlassCreateForm
    success_url = reverse_lazy('dashboard')
    ALL_ORDERS = []

    def post(self, request, *args, **kwargs):
        form = GlassCreateForm(request.POST)
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

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

                context = {
                    'form': form,
                    'all_orders': ALL_ORDERS,
                }

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
                    note = 'test',
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
    pass


class GlassDetailsView(DetailView):
    pass


class GlassUpdateView(UpdateView):
    pass


class GlassDeleteView(DeleteView):
    pass