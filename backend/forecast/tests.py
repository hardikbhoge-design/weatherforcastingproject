from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CitySearchHistory, UserFavoriteCity
from .weather_service import get_wmo_info, wind_direction_to_cardinal, generate_smart_recommendations
from .ai_engine import engineer_features, calculate_heuristic_prob, generate_synthetic_weather_dataset


class WeatherServiceTestCase(TestCase):
    def test_wmo_mapping(self):
        info_clear = get_wmo_info(0, is_day=1)
        self.assertEqual(info_clear["category"], "clear")
        self.assertEqual(info_clear["icon"], "clear")

        info_rain = get_wmo_info(65, is_day=1)
        self.assertEqual(info_rain["category"], "rain")

        info_thunder = get_wmo_info(95, is_day=1)
        self.assertEqual(info_thunder["category"], "thunderstorm")

    def test_wind_direction_cardinals(self):
        self.assertEqual(wind_direction_to_cardinal(0), "N")
        self.assertEqual(wind_direction_to_cardinal(90), "E")
        self.assertEqual(wind_direction_to_cardinal(180), "S")
        self.assertEqual(wind_direction_to_cardinal(270), "W")

    def test_smart_recommendations(self):
        current_wet = {
            "temperature": 18,
            "precipitation": 2.5,
            "precipitation_probability": 80,
            "wind_speed": 15,
            "uv_index": 2
        }
        hourly = [{"precip_prob": 85} for _ in range(6)]
        recs = generate_smart_recommendations(current_wet, hourly)
        types = [r["type"] for r in recs]
        self.assertIn("umbrella", types)
        self.assertIn("clothing", types)


class AIEngineTestCase(TestCase):
    def test_feature_engineering(self):
        df_syn = generate_synthetic_weather_dataset()
        df_feat = engineer_features(df_syn)
        
        self.assertIn("dew_point_spread", df_feat.columns)
        self.assertIn("temp_diff_3h", df_feat.columns)
        self.assertIn("pressure_diff_3h", df_feat.columns)
        self.assertIn("hour_sin", df_feat.columns)
        self.assertIn("hour_cos", df_feat.columns)

    def test_heuristic_fallback(self):
        prob_high = calculate_heuristic_prob(humidity=95, cloud_cover=90, pressure_trend=-3.5)
        prob_low = calculate_heuristic_prob(humidity=20, cloud_cover=10, pressure_trend=1.5)
        self.assertGreater(prob_high, prob_low)


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testpilot", password="password123", email="test@pilot.com")

    def test_login_page_renders(self):
        response = self.client.get(reverse('forecast:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign In")
        self.assertContains(response, "Create Account")
        self.assertContains(response, "1-Click Demo Login")

    def test_login_success(self):
        response = self.client.post(reverse('forecast:login'), {
            'action': 'login',
            'username': 'testpilot',
            'password': 'password123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testpilot")

    def test_login_failure(self):
        response = self.client.post(reverse('forecast:login'), {
            'action': 'login',
            'username': 'testpilot',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

    def test_registration_flow(self):
        response = self.client.post(reverse('forecast:login'), {
            'action': 'register',
            'reg_username': 'newuser123',
            'reg_email': 'newuser@example.com',
            'reg_password': 'securepass123',
            'reg_confirm_password': 'securepass123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser123').exists())

    def test_demo_login(self):
        response = self.client.get(reverse('forecast:demo_login'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "weather_pilot")

    def test_logout(self):
        self.client.login(username='testpilot', password='password123')
        response = self.client.get(reverse('forecast:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "signed out")

    def test_favorite_toggle_api(self):
        # Unauthenticated request
        response = self.client.post(reverse('forecast:api_toggle_favorite'), 
                                    data='{"city_name":"Paris","country":"France","latitude":48.85,"longitude":2.35}', 
                                    content_type="application/json")
        self.assertEqual(response.status_code, 401)

        # Authenticated request
        self.client.login(username='testpilot', password='password123')
        response = self.client.post(reverse('forecast:api_toggle_favorite'), 
                                    data='{"city_name":"Paris","country":"France","latitude":48.85,"longitude":2.35}', 
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_favorited"])
        self.assertTrue(UserFavoriteCity.objects.filter(user=self.user, city_name="Paris").exists())


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="viewer", password="password123")

    def test_index_view_unauthenticated_redirects_to_login(self):
        # Default link access without login redirects to login portal
        response = self.client.get(reverse('forecast:index'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SYNOPTIC")
        self.assertContains(response, "Sign In")

    def test_index_view_guest_access(self):
        # Guest access directly opens dashboard
        response = self.client.get(reverse('forecast:index') + '?guest=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chance of rain")
        self.assertContains(response, "Global map")
        self.assertContains(response, "Other large cities")

    def test_api_city_search(self):
        response = self.client.get(reverse('forecast:api_city_search') + '?q=Lon')
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("results", json_data)



