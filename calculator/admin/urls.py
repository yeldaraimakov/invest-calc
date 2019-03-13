from django.urls import path
from django.contrib.auth.views import logout_then_login

from calculator.admin import views


urlpatterns = [
    path('', views.FilesListView.as_view(), name='admin_home'),
    path('logout/', logout_then_login, name="logout"),
]
