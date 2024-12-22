from django.urls import path, include
from nadejda_94_django.records.views import RecordCreateView

urlpatterns = [
    path('<int:partner_pk>/records/', include([
        path('create/', RecordCreateView.as_view(), name='record_create'),
        ])
    )]