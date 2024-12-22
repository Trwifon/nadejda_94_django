from django import forms
from django.forms import ModelForm
from nadejda_94_django.records.models import Partner


class PartnerForm(ModelForm):
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all().order_by('name'),
        label='Фирма',
    )

    class Meta:
        model = Partner
        fields = ['partner']