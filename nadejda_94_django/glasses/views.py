from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from nadejda_94_django.glasses.forms import GlassCreateForm
from nadejda_94_django.glasses.models import Glasses, Partner, Record
from nadejda_94_django.records.views import OrderCreateView

all_order = []
class GlassCreateView(OrderCreateView):
    model = Glasses
    template_name = 'glasses/create_glass.html'
    permission_required = 'glasses.add_glasses'
    form_class = GlassCreateForm
    success_url = reverse_lazy('dashboard')
    all_order = []

    def post(self, request, *args, **kwargs):
        form = GlassCreateForm(request.POST)
        current_pk = kwargs.get('partner_pk')
        current_partner = Partner.objects.get(pk=current_pk)

        if form.is_valid():
            current_order = form.cleaned_data
            all_order.append(current_order)

            context = {
                'form': form,
                'all_order': all_order,
                'partner': current_partner,
            }

            return render(request, 'glasses/create_glass.html', context)











class GlassListView(ListView):
    pass


class GlassDetailsView(DetailView):
    pass


class GlassUpdateView(UpdateView):
    pass


class GlassDeleteView(DeleteView):
    pass