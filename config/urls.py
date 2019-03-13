from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('calculator.main_app.urls')),
    path('admin/', include('calculator.admin.urls')),
    path('admin/', admin.site.urls),
]
