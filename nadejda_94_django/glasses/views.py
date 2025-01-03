from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView


class GlassCreateView(CreateView):
    pass

class GlassListView(ListView):
    pass


class GlassDetailsView(DetailView):
    pass


class GlassUpdateView(UpdateView):
    pass


class GlassDeleteView(DeleteView):
    pass