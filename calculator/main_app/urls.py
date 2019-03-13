from django.urls import path
from calculator.main_app import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="main_app/home.html"), name='home'),
    path('faq/', TemplateView.as_view(template_name="main_app/faq.html"), name='faq'),
    path('download/', views.download, name='download'),
]
