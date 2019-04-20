from django.urls import path
from calculator.main_app import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="main_app/home.html"), name='home'),
    path('faq/', TemplateView.as_view(template_name="main_app/faq.html"), name='faq'),
    path('charts/', views.charts, name='charts'),
    path('download-excel/', views.download_excel, name='download_excel'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('registration/', views.RegistrationFormView.as_view(), name='registration'),
]
