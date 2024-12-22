from django.urls import path
from nadejda_94_django.common.views import Dashboard


urlpatterns = [
    path('', Dashboard.as_view(), name='dashboard'),
]