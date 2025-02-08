from django.urls import path, include
from nadejda_94_django.glasses.views import GlassCreateView, GlassUpdateView, GlassDeleteView, \
    GlassListView, GlassProductionView, ExcelGlassView

urlpatterns = [
    path('<int:partner_pk>/<str:note>/create/', GlassCreateView.as_view(), name='glass_create'),
    path('<int:record_pk>/', include([
        path('details/', GlassListView.as_view(), name='glass_details'),
        path('update/<int:pk>/', GlassUpdateView.as_view(), name='glass_update'),
        path('delete/', GlassDeleteView.as_view(), name='glass_delete'),
    ])),
    path('production/', GlassProductionView.as_view(), name='glass_production'),
    path('excel/<str:sent_pk>/', ExcelGlassView.as_view(), name='glass_excel'),
]

