from django.urls import path, include
from nadejda_94_django.records.views import RecordCreateView, ReportsCreateView, ReportShowView

urlpatterns = [
    path('create-report', ReportsCreateView.as_view(), name='create_report'),
    path('show-report', ReportShowView.as_view(), name='show_report'),
    path('<int:partner_pk>/records/', include([
        path('create/', RecordCreateView.as_view(), name='record_create'),
        ])
    )]