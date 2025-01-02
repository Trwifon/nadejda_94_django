from django.urls import path, include
from nadejda_94_django.records.views import RecordCreateView, ReportsCreateView, ReportShowView, CashShowView, \
    RecordUpdateView, PartnerCreateView, ErrorTestView

urlpatterns = [
    path('create-report', ReportsCreateView.as_view(), name='create_report'),
    path('show-report', ReportShowView.as_view(), name='show_report'),
    path('cash-report', CashShowView.as_view(), name='cash_report'),
    path('partner-create', PartnerCreateView.as_view(), name='partner_create'),
    path('errors-test', ErrorTestView.as_view(), name='errors_test'),

    path('<int:partner_pk>/create', RecordCreateView.as_view(), name='record_create'),
    path('<int:record_pk>/update', RecordUpdateView.as_view(), name='record_update'),
    ]