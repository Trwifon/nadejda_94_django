from django.shortcuts import render, redirect
from django.views.generic import CreateView
from nadejda_94_django.records.forms import RecordCreateForm
from nadejda_94_django.records.helpers import get_close_balance, get_order, update_order
from nadejda_94_django.records.models import Record, Partner

users_dict = {'Trifon': 'M', 'Tsonka': 'O', 'Elena': 'A', 'Diana': 'P', 'Nadya': 'G'}


class RecordCreateView(CreateView):
    model = Record
    form_class = RecordCreateForm
    template_name = 'records/create_record.html'
    # fields = ['order_type', 'amount', 'note']

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
                'firm_report': firm_report,
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
                    'firm_report': firm_report,
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





