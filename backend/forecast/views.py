import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .weather_service import geocode_city, reverse_geocode, fetch_weather_forecast, calculate_air_quality_index, fetch_benchmark_cities_weather
from .ai_engine import predict_weather_ai, train_ai_model, get_model_cache_path
from .models import CitySearchHistory, UserFavoriteCity


DEFAULT_CITY = "London"
DEFAULT_LAT = 51.5074
DEFAULT_LON = -0.1278
DEFAULT_COUNTRY = "United Kingdom"


def get_location_and_weather(city_query=None, lat=None, lon=None, user=None):
    """Helper to resolve coordinates and retrieve full weather + AI prediction data."""
    city_name = DEFAULT_CITY
    country = DEFAULT_COUNTRY
    latitude = DEFAULT_LAT
    longitude = DEFAULT_LON
    timezone_str = "auto"
    
    if lat is not None and lon is not None:
        try:
            latitude = float(lat)
            longitude = float(lon)
            rev_city, rev_country = reverse_geocode(latitude, longitude)
            city_name = rev_city
            country = rev_country
        except ValueError:
            pass
    elif city_query and city_query.strip():
        locations = geocode_city(city_query)
        if locations:
            top = locations[0]
            city_name = top["name"]
            country = top["country"]
            latitude = top["latitude"]
            longitude = top["longitude"]
            timezone_str = top.get("timezone", "auto")
            
            # Save to search history
            try:
                auth_user = user if (user and user.is_authenticated) else None
                CitySearchHistory.objects.create(
                    user=auth_user,
                    city_name=city_name,
                    country=country,
                    latitude=latitude,
                    longitude=longitude
                )
            except Exception:
                pass
        else:
            return None, f"City '{city_query}' could not be found. Please try another location."

    # Fetch real-time and forecast weather
    weather_data = fetch_weather_forecast(latitude, longitude, timezone_str)
    if not weather_data:
        return None, "Failed to retrieve meteorological data. Please check your connection."
        
    # Generate AI predictions
    ai_predictions = predict_weather_ai(latitude, longitude, weather_data)
    
    # Calculate Air Quality Index
    air_quality = calculate_air_quality_index(
        weather_data["current"]["humidity"],
        weather_data["current"]["wind_speed"],
        weather_data["current"]["temperature"]
    )

    full_payload = {
        "location": {
            "city": city_name,
            "country": country,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_str
        },
        "current": weather_data["current"],
        "hourly": weather_data["hourly"],
        "daily": weather_data["daily"],
        "recommendations": weather_data["recommendations"],
        "air_quality": air_quality,
        "enhancements": weather_data.get("enhancements", {}),
        "ai": ai_predictions
    }
    
    return full_payload, None


def index(request):
    """Main dashboard view rendering complete weather data and AI forecast."""
    # If user explicitly accessed with ?guest=1 or is searching, preserve guest session
    if request.GET.get('guest'):
        request.session['is_guest'] = True

    is_guest = request.session.get('is_guest', False) or bool(request.GET.get('guest')) or bool(request.GET.get('city')) or bool(request.GET.get('lat'))
    if not request.user.is_authenticated and not is_guest:
        return redirect('forecast:login')

    city_query = request.GET.get('city', '').strip()
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not city_query and not lat:
        # Check if logged in user has a favorite city to load as default
        if request.user.is_authenticated:
            top_fav = request.user.favorite_cities.first()
            if top_fav:
                city_query = top_fav.city_name
                lat = top_fav.latitude
                lon = top_fav.longitude
        if not city_query and not lat:
            city_query = DEFAULT_CITY
        
    data, error = get_location_and_weather(city_query=city_query, lat=lat, lon=lon, user=request.user)
    
    # Benchmark cities for 'Other large cities' sidebar
    other_cities = fetch_benchmark_cities_weather()

    # Recent search history for quick chips
    if request.user.is_authenticated:
        recent_searches = CitySearchHistory.objects.filter(user=request.user).values('city_name', 'country').distinct()[:6]
        if not recent_searches.exists():
            recent_searches = CitySearchHistory.objects.values('city_name', 'country').distinct()[:6]
    else:
        recent_searches = CitySearchHistory.objects.values('city_name', 'country').distinct()[:6]

    # User favorite cities
    favorite_cities = []
    is_current_favorite = False
    if request.user.is_authenticated:
        favorite_cities = list(request.user.favorite_cities.values('city_name', 'country', 'latitude', 'longitude'))
        if data:
            current_city = data["location"]["city"]
            current_country = data["location"]["country"]
            is_current_favorite = request.user.favorite_cities.filter(
                city_name__iexact=current_city
            ).exists()

    context = {
        "data": data,
        "data_json": json.dumps(data) if data else "{}",
        "other_cities": other_cities,
        "error": error,
        "query": city_query,
        "recent_searches": recent_searches,
        "favorite_cities": favorite_cities,
        "is_current_favorite": is_current_favorite,
    }
    return render(request, "index.html", context)


def login_view(request):
    """Front Login & Registration portal page."""
    if request.user.is_authenticated:
        return redirect('forecast:index')

    tab = request.GET.get('tab', 'login')
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        action = request.POST.get('action', 'login')
        next_url = request.POST.get('next', '') or '/'

        if action == 'login':
            username_val = request.POST.get('username', '').strip()
            password_val = request.POST.get('password', '')

            if not username_val or not password_val:
                messages.error(request, "Please provide both username/email and password.")
                return render(request, "login.html", {"active_tab": "login", "next": next_url, "username": username_val})

            # Check if user passed an email address instead of username
            actual_username = username_val
            if '@' in username_val:
                user_match = User.objects.filter(email__iexact=username_val).first()
                if user_match:
                    actual_username = user_match.username

            user = authenticate(request, username=actual_username, password=password_val)
            if user is None and actual_username != username_val:
                # Also try direct authentication with username_val in case username itself has an '@'
                user = authenticate(request, username=username_val, password=password_val)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}! Real-time AI forecast loaded.")
                return redirect(next_url if next_url.startswith('/') else 'forecast:index')
            else:
                messages.error(request, "Invalid username or password. Please verify your credentials or use 1-Click Demo Login.")
                return render(request, "login.html", {"active_tab": "login", "next": next_url, "username": username_val})

        elif action == 'register':
            username_val = request.POST.get('reg_username', '').strip()
            email_val = request.POST.get('reg_email', '').strip()
            password_val = request.POST.get('reg_password', '')
            confirm_password_val = request.POST.get('reg_confirm_password', '')

            if not username_val or not password_val:
                messages.error(request, "Username and password are required.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            if len(username_val) < 3:
                messages.error(request, "Username must be at least 3 characters long.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            if password_val != confirm_password_val:
                messages.error(request, "Passwords do not match. Please enter them carefully.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            if len(password_val) < 6:
                messages.error(request, "Password should be at least 6 characters long.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            if User.objects.filter(username__iexact=username_val).exists():
                messages.error(request, f"Username '{username_val}' is already taken. Please choose another.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            if email_val and User.objects.filter(email__iexact=email_val).exists():
                messages.error(request, f"An account with email '{email_val}' already exists. Please sign in or use another email.")
                return render(request, "login.html", {"active_tab": "register", "next": next_url, "reg_username": username_val, "reg_email": email_val})

            user = User.objects.create_user(username=username_val, email=email_val, password=password_val)
            login(request, user)
            messages.success(request, f"Account successfully created! Welcome to WeatherAI V2, {user.username}.")
            return redirect('forecast:index')

    return render(request, "login.html", {
        "active_tab": tab,
        "next": next_url
    })


def register_view(request):
    """Direct alias or POST handler for registration."""
    if request.user.is_authenticated:
        return redirect('forecast:index')
    return redirect('/login/?tab=register')


def logout_view(request):
    """Log out authenticated user and redirect with message."""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"You have been signed out. See you next time, {username}!")
    return redirect('forecast:login')


def demo_login_view(request):
    """One-click instant demo login for reviewers and test users."""
    demo_username = "weather_pilot"
    demo_pass = "DemoForecast2026!"
    
    user = User.objects.filter(username=demo_username).first()
    if not user:
        user = User.objects.create_user(
            username=demo_username,
            email="pilot@weatherai.internal",
            password=demo_pass,
            first_name="Weather",
            last_name="Explorer"
        )
        # Seed sample favorite cities for demo pilot
        UserFavoriteCity.objects.get_or_create(
            user=user,
            city_name="London",
            defaults={"country": "United Kingdom", "latitude": 51.5074, "longitude": -0.1278}
        )
        UserFavoriteCity.objects.get_or_create(
            user=user,
            city_name="Tokyo",
            defaults={"country": "Japan", "latitude": 35.6895, "longitude": 139.6917}
        )
        UserFavoriteCity.objects.get_or_create(
            user=user,
            city_name="San Francisco",
            defaults={"country": "United States", "latitude": 37.7749, "longitude": -122.4194}
        )

    login(request, user)
    messages.success(request, "Logged in with Demo Pilot Account! Sample favorite cities loaded.")
    return redirect('forecast:index')


@require_POST
def api_toggle_favorite(request):
    """Toggle a city bookmark in user's favorites list."""
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Authentication required to bookmark cities."}, status=401)
    
    try:
        body = json.loads(request.body)
        city_name = body.get('city_name', '').strip()
        country = body.get('country', '').strip()
        latitude = float(body.get('latitude', 0))
        longitude = float(body.get('longitude', 0))
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid request payload."}, status=400)

    if not city_name:
        return JsonResponse({"status": "error", "message": "City name is required."}, status=400)

    existing = UserFavoriteCity.objects.filter(user=request.user, city_name__iexact=city_name).first()
    if existing:
        existing.delete()
        is_favorited = False
        msg = f"Removed {city_name} from your bookmarks."
    else:
        UserFavoriteCity.objects.create(
            user=request.user,
            city_name=city_name,
            country=country,
            latitude=latitude,
            longitude=longitude
        )
        is_favorited = True
        msg = f"Added {city_name} to your bookmarks!"

    fav_list = list(request.user.favorite_cities.values('city_name', 'country', 'latitude', 'longitude'))

    return JsonResponse({
        "status": "success",
        "is_favorited": is_favorited,
        "message": msg,
        "favorites": fav_list
    })


@require_GET
def api_forecast(request):
    """JSON API endpoint for fetching weather & AI forecast dynamically."""
    city_query = request.GET.get('city', '').strip()
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not city_query and not lat:
        city_query = DEFAULT_CITY

    data, error = get_location_and_weather(city_query=city_query, lat=lat, lon=lon, user=request.user)
    if error:
        return JsonResponse({"status": "error", "message": error}, status=400)
        
    return JsonResponse({"status": "success", "data": data})


@require_GET
def api_city_search(request):
    """JSON API for city autocomplete suggestions."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({"results": []})
        
    results = geocode_city(query)
    return JsonResponse({"results": results})


@csrf_exempt
@require_POST
def api_train_model(request):
    """Trigger background model retraining for a specific location."""
    try:
        body = json.loads(request.body)
        lat = float(body.get('lat', DEFAULT_LAT))
        lon = float(body.get('lon', DEFAULT_LON))
    except Exception:
        lat, lon = DEFAULT_LAT, DEFAULT_LON
        
    bundle = train_ai_model(lat, lon)
    return JsonResponse({
        "status": "success",
        "message": "AI Model trained and serialized successfully.",
        "f1_score": bundle["f1_score"],
        "samples": bundle["samples"],
        "trained_at": bundle["trained_at"]
    })


def service_worker_view(request):
    """Serve the service worker script with correct JavaScript MIME type."""
    from django.http import HttpResponse
    import os
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'sw.js')
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/javascript')
    except Exception:
        return HttpResponse("// Service worker placeholder", content_type='application/javascript')


@require_GET
def api_check_weather_alerts(request):
    """
    Background polling API endpoint for detecting real-time weather transitions:
    - Rain approaching / Rain starting
    - Rain cleared / Sky opening
    - Cloud cover sudden increase (overcast)
    - Heat surge (> 35°C or rapid spike)
    """
    try:
        lat = float(request.GET.get('lat', DEFAULT_LAT))
        lon = float(request.GET.get('lon', DEFAULT_LON))
        city = request.GET.get('city', 'Your Location')
        
        last_temp = float(request.GET.get('last_temp', 0)) if request.GET.get('last_temp') else None
        last_precip = float(request.GET.get('last_precip', 0)) if request.GET.get('last_precip') else None
        last_cloud = int(request.GET.get('last_cloud', 0)) if request.GET.get('last_cloud') else None
        last_code = int(request.GET.get('last_code', 0)) if request.GET.get('last_code') else None
    except Exception:
        return JsonResponse({"status": "error", "message": "Invalid parameters"}, status=400)

    weather_data = fetch_weather_forecast(lat, lon, timezone_str="auto")
    if not weather_data:
        return JsonResponse({"status": "error", "message": "Failed to fetch weather"}, status=500)

    curr = weather_data["current"]
    hourly = weather_data.get("hourly", [])
    
    current_temp = curr.get("temperature", 20.0)
    current_precip = curr.get("precipitation", 0.0)
    current_prob = curr.get("precipitation_probability", 0)
    current_cloud = curr.get("cloud_cover", 0)
    current_code = curr.get("weather_code", 0)
    
    next_3h_max_rain_prob = max([h.get("precip_prob", 0) for h in hourly[:3]], default=0)

    alerts = []

    # 1. Rain Approaching or Started
    if (current_precip > 0.2 or current_prob >= 60 or next_3h_max_rain_prob >= 65) and (last_precip is None or last_precip == 0.0):
        alerts.append({
            "type": "rain_start",
            "title": f"🌧️ Rain Alert in {city}!",
            "body": f"Precipitation detected ({int(current_prob)}% probability). Carry an umbrella if stepping outside!",
            "tag": f"rain-alert-{city}"
        })

    # 2. Rain Cleared / Dry Conditions Resumed
    if (last_precip is not None and last_precip > 0.2) and current_precip == 0.0 and current_prob < 20:
        alerts.append({
            "type": "rain_cleared",
            "title": f"🌤️ Rain Stopped in {city}!",
            "body": f"The skies are clearing up with dry conditions ahead. Great time to go outdoors!",
            "tag": f"rain-cleared-{city}"
        })

    # 3. Sudden Cloud Cover / Overcast Surge
    if current_cloud >= 75 and (last_cloud is not None and last_cloud < 45):
        alerts.append({
            "type": "cloudy_surge",
            "title": f"☁️ Overcast Alert in {city}",
            "body": f"Dense cloud cover rolling in ({current_cloud}% cover). Expect reduced sunlight and mild cooling.",
            "tag": f"cloud-alert-{city}"
        })

    # 4. High Heat / Temperature Spike
    if current_temp >= 35.0:
        alerts.append({
            "type": "heat_surge",
            "title": f"🔥 High Heat Warning in {city}!",
            "body": f"Surface temperature has reached {current_temp}°C. Stay hydrated and avoid direct peak sun.",
            "tag": f"heat-alert-{city}"
        })
    elif last_temp is not None and (current_temp - last_temp >= 4.0):
        alerts.append({
            "type": "temp_spike",
            "title": f"🌡️ Rapid Warming Alert in {city}",
            "body": f"Temperature jumped by +{round(current_temp - last_temp, 1)}°C up to {current_temp}°C.",
            "tag": f"temp-spike-{city}"
        })

    return JsonResponse({
        "status": "success",
        "alerts": alerts,
        "current_state": {
            "temp": current_temp,
            "precip": current_precip,
            "precip_prob": current_prob,
            "cloud_cover": current_cloud,
            "weather_code": current_code,
            "weather_desc": curr.get("weather_description", "Clear")
        }
    })


