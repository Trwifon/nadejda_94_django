from datetime import datetime
from django.forms import ModelForm
from django import forms
from .choices import WarehouseChoices, ReportChoices
from .models import Record, Partner


class RecordCreateForm(ModelForm):
    class Meta:
        model = Record
        fields = [
            'order_type',
            'amount',
            'note',
        ]

        labels = {
            'order_type': 'Вид',
            'amount': 'Сума',
            'note': 'Забележка'
        }


class PartnerForm(ModelForm):
    partner = forms.ModelChoiceField(
    queryset=Partner.objects.all().order_by('name'),
    label='Фирма',
    )
    class Meta:
        model = Partner
        fields = ['partner']


class NewPartnerForm(ModelForm):
    class Meta:
        model = Partner
        exclude = ['type']
        labels = {
            'name': 'Име',
            'balance': 'Салдо',
        }


class ReportsCreateForm(forms.Form):

    report_field = forms.ChoiceField(
        choices = ReportChoices.choices,
        label='Вид отчет: '
    )

    firm_field = forms.ModelChoiceField(
        queryset=Partner.objects.all().order_by('name'),
        label='Фирма',
        required=False,
    )

    warehouse = forms.ChoiceField(
        choices=WarehouseChoices.choices,
        label='Склад: '
    )

    date_field = forms.DateField(
        widget=forms.SelectDateWidget(),
        label='Дата: '
    )


    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial.setdefault('report_field', 'FR')
        initial.setdefault('date_field', datetime.now().date())
        initial.setdefault('firm_field', Partner.objects.get(id=2))
        super(ReportsCreateForm, self).__init__(*args, **kwargs)
        self.initial = initial
