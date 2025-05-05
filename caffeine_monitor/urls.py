from django.contrib import admin
from django.urls import path, include  # ✅ Include 'include' to link app URLs

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('monitoring.urls')),  # ✅ Link to monitoring/urls.py
]
