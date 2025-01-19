from django.urls import path, include
from nadejda_94_django.glasses.views import GlassCreateView, GlassUpdateView, GlassDeleteView, \
    GlassListView

urlpatterns = [
    path('<int:partner_pk>/<str:note>/create/', GlassCreateView.as_view(), name='glass_create'),
    path('<int:record_pk>/', include([
        path('details/', GlassListView.as_view(), name='glass_details'),
        path('update/', GlassUpdateView.as_view(), name='glass_update'),
        path('delete/', GlassDeleteView.as_view(), name='glass_delete'),
    ])),
]