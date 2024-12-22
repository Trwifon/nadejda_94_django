from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from nadejda_94_django.mixins import ReadonlyViewMixin

UserModel = get_user_model()


class ProfileBaseForm(forms.ModelForm):
    username = forms.CharField(
        max_length=30,
        help_text='Въведете потребителско име',
        widget=forms.TextInput(attrs={'placeholder': 'Потребителско име'}))

    first_name = forms.CharField(
        max_length=30,
        help_text='Въведете име',
        widget=forms.TextInput(attrs={'placeholder': 'Име'}))

    last_name = forms.CharField(
        max_length=30,
        help_text='Въведете фамилия',
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name', 'email')


class ProfileCreateForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        help_text= 'Потребителското име трябва да съдържа само букви и цифри',
        widget=forms.TextInput(attrs={'placeholder': 'Потребитеслко име'}))

    email = forms.EmailField(
        help_text='Въведете Вашия имейл',
        widget=forms.TextInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = UserModel
        fields = ('username', 'email')


class ProfileUpdateForm(ProfileBaseForm):
    pass


class DeleteUserForm(ReadonlyViewMixin, ProfileBaseForm):
    read_only_fields = ('username', 'first_name', 'last_name')

    class Meta:
        model = UserModel
        fields = ('username', 'first_name', 'last_name')