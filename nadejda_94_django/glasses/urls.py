from django.urls import path, include
from nadejda_94_django.glasses.views import GlassCreateView, GlassDetailsView, GlassUpdateView, GlassDeleteView

urlpatterns = [
    path('<int:partner_pk>/create/', GlassCreateView.as_view(), name='glass_create'),
    path('<int:glass_pk>', include([
        path('details/', GlassDetailsView.as_view, name='glass_details'),
        path('update/', GlassUpdateView.as_view(), name='glass_update'),
        path('delete/', GlassDeleteView.as_view(), name='glass_delete'),
        
    ])),
]