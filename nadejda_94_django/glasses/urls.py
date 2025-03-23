from django.urls import path, include, re_path
from nadejda_94_django.glasses.views import (GlassCreateView, GlassUpdateView, GlassDeleteView, \
    GlassListView, GlassProductionView, ExcelGlassView, PGlassCreateView, RecordPriceIncreaseView,)

urlpatterns = [
    path('<int:partner_pk>/<str:note>/create/', GlassCreateView.as_view(), name='glass_create'),
    path('<int:record_pk>/<str:note>/p_create/', PGlassCreateView.as_view(), name='p_glass_create'),
    path('<int:record_pk>/', include([
        path('details/', GlassListView.as_view(), name='glass_details'),
        path('update/<int:pk>/<int:old_total>', GlassUpdateView.as_view(), name='glass_update'),
        path('delete/', GlassDeleteView.as_view(), name='glass_delete'),
        re_path(r'record-price-increase/(?P<diff>-?[0-9]+)/(?P<to_update>[^/]+)$',
                RecordPriceIncreaseView.as_view(),
                name='record_price_increase'),
    ])),
    path('production/', GlassProductionView.as_view(), name='glass_production'),
    path('excel/<str:sent_time>/', ExcelGlassView.as_view(), name='glass_excel'),
]

