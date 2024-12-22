from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, FormView
from nadejda_94_django.accounts.forms import ProfileCreateForm, ProfileUpdateForm, DeleteUserForm
from nadejda_94_django.accounts.models import User

UserModel = get_user_model()


class UserRegisterView(CreateView):
    model = UserModel
    form_class = ProfileCreateForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('dashboard')


class UserDetailsView(LoginRequiredMixin, DetailView):
    model = UserModel
    template_name = 'accounts/profile_details.html'
    context_object_name = 'profile'
    login_url = reverse_lazy('login')


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = UserModel
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('dashboard')
    login_url = reverse_lazy('login')

    def test_func(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return self.request.user == user


class UserDeleteView(UserPassesTestMixin, DeleteView, FormView):
    model = UserModel
    form_class = DeleteUserForm
    template_name = 'accounts/profile_delete.html'
    success_url = reverse_lazy('dashboard')
    login_url = reverse_lazy('login')

    def get_initial(self):
        return self.object.__dict__

    def form_invalid(self, form):
        return self.form_valid(form)

    def test_func(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        authorization = self.request.user == user or self.request.user.has_perm('account.delete_account')
        return authorization

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)
