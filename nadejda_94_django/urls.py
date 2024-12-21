from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nadejda_94_django.common.urls')),
    path('', include('nadejda_94_django.records.urls')),
    path('', include('nadejda_94_django.accounts.urls')),

]
