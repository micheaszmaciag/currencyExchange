from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRoutes),
    path('currency/<str:base_currency>/<str:quote_currency>/', views.getCurrencyRate, name='getCurrencyRate'),
]