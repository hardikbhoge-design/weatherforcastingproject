from django.contrib import admin
from .models import CitySearchHistory, UserFavoriteCity


@admin.register(CitySearchHistory)
class CitySearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('city_name', 'country', 'user', 'latitude', 'longitude', 'searched_at')
    search_fields = ('city_name', 'country', 'user__username')
    list_filter = ('searched_at', 'user')


@admin.register(UserFavoriteCity)
class UserFavoriteCityAdmin(admin.ModelAdmin):
    list_display = ('user', 'city_name', 'country', 'latitude', 'longitude', 'created_at')
    search_fields = ('city_name', 'country', 'user__username')
    list_filter = ('created_at', 'user')

