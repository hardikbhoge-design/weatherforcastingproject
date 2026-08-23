from django.db import models
from django.contrib.auth.models import User


class CitySearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='search_history')
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'City Search Histories'

    def __str__(self):
        user_str = f" [{self.user.username}]" if self.user else ""
        return f"{self.city_name}, {self.country}{user_str} ({self.searched_at:%Y-%m-%d %H:%M})"


class UserFavoriteCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_cities')
    city_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'city_name', 'country')
        verbose_name_plural = 'User Favorite Cities'

    def __str__(self):
        return f"{self.user.username} ★ {self.city_name}, {self.country}"

