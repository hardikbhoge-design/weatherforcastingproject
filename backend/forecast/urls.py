"""
URL patterns for the forecast application.
"""
from django.urls import path
from . import views

app_name = 'forecast'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('demo-login/', views.demo_login_view, name='demo_login'),
    path('api/forecast/', views.api_forecast, name='api_forecast'),
    path('api/search-cities/', views.api_city_search, name='api_city_search'),
    path('api/city-search/', views.api_city_search, name='api_city_search_alt'),
    path('api/train/', views.api_train_model, name='api_train_model'),
    path('api/toggle-favorite/', views.api_toggle_favorite, name='api_toggle_favorite'),
    path('api/check-weather-alerts/', views.api_check_weather_alerts, name='api_check_weather_alerts'),
    path('sw.js', views.service_worker_view, name='service_worker'),
]

