from django import forms
from django.core.validators import MinValueValidator
from django.forms import ChoiceField
from nadejda_94_django.glasses.models import Glasses
from .choices import ThicknessChoices, GlassChoices


class GlassBaseForm(forms.ModelForm):
    class Meta:
        model = Glasses
        fields = [
            'first_glass',
            'second_glass',
            'third_glass',
            'thickness',
            'unit_price',
            'width',
            'height',
            'number',
        ]
        labels = {
            'first_glass': 'Първо стъкло',
            'second_glass': 'Второ стъкло',
            'third_glass': 'Трето стъкло',
            'thickness': 'Дебелина',
            'unit_price': 'Единична цена',
            'width': 'Първи размер',
            'height': 'Втори размер',
            'number': 'Брой',
        }

    def __init__(self, *args, **kwargs):
        super(GlassBaseForm, self).__init__(*args, **kwargs)
        self.fields['unit_price'].widget.attrs['min'] = 5
        self.fields['width'].widget.attrs['min'] = 8
        self.fields['width'].widget.attrs['max'] = 3210
        self.fields['height'].widget.attrs['min'] = 8
        self.fields['height'].widget.attrs['max'] = 3210
        self.fields['number'].widget.attrs['min'] = 1


class GlassCreateForm(GlassBaseForm):
    pass


class PGlassCreateForm(GlassBaseForm):
    pass


class GlassUpdateForm(GlassBaseForm):

    class Meta(GlassBaseForm.Meta):
        fields = GlassBaseForm.Meta.fields + [
            'module',
            'supplement',
        ]
        labels = GlassBaseForm.Meta.labels | {
            'module': 'Модул',
            'supplement': 'Добавка',
        }

    def __init__(self, *args, **kwargs):
        super(GlassBaseForm, self).__init__(*args, **kwargs)
        self.fields['number'].widget.attrs['min'] = 0


class GlassDeleteForm(GlassBaseForm):
    class Meta:
        model = Glasses
        fields = []


class GlassProductionForm(forms.Form):
    order_choice = forms.ChoiceField(
        label='Избери поръчка',
        widget=forms.RadioSelect,
    )


class RecordsPriceIncrease(forms.Form):
    pass
