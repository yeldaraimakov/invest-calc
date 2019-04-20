from django.urls import path

from calculator.admin import views


urlpatterns = [
    path('', views.FilesListView.as_view(), name='admin_home'),
]
