from django.urls import path
from . import views


urlpatterns = [
    path('', views.getRoutes),
    path('currency/', views.getCurrency),
    path('currency/<str:currency>/<str:second>/', views.getCurrencyRate),
]