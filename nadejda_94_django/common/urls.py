from django.urls import path
from nadejda_94_django.common.views import Dashboard

urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
    # path('export/', ExportToExcelView.as_view(), name='export_to_excel'),
]