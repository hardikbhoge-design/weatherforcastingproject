# Advanced Real-Time Weather Forecasting V2 with AI & Django

A production-grade AI-powered real-time weather forecasting web application built with **Python**, **Django**, **Scikit-Learn (`HistGradientBoostingClassifier`)**, and **Open-Meteo APIs**.

![AI Weather Forecasting](https://img.shields.io/badge/Python-3.14-blue)
![Django](https://img.shields.io/badge/Django-5.0+-green)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-HistGradientBoosting-orange)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-purple)

---

## 🌟 Key Features

1. **AI Rain Probability Prediction Engine**:
   - Analyzes real-time & historical meteorological parameters (surface pressure, temperature trends, dew point spread, humidity, wind, cyclical hour/day sine-cosine features).
   - Powered by `HistGradientBoostingClassifier` with `class_weight='balanced'` and `TimeSeriesSplit` cross-validation.
   - Outputs 1 to 6-hour forward rain probability timeline with risk levels (Low, Moderate, High, Severe).
   - High-performance caching with `joblib` and thread/process-safe concurrency using `FileLock`.

2. **Real-Time Data Integration**:
   - Geocoding API with fast autocomplete city suggestions and GPS Geolocation.
   - Open-Meteo Current & 7-Day Hourly Forecast API (free, reliable, global).
   - 3-hour Barometric Pressure Trend calculation (Rising ↗, Falling ↘, Steady →).

3. **Ultra-Modern Glassmorphic UI**:
   - Animated SVG AI Rain Probability circular gauge.
   - 24-hour dual-axis interactive temperature & rain chance chart with **Chart.js**.
   - 7-Day extended forecast with dynamic temperature range bars.
   - Comprehensive weather metrics: Humidity & Dew Point, Wind Compass, Barometric Pressure, UV Index Meter, Visibility & Cloud Cover, Sunrise & Sunset schedule.
   - Smart weather lifestyle recommendations (Umbrella Alert, Clothing advice, Outdoor activity suitability, UV protection).
   - Dynamic weather-reactive themes (Clear, Cloudy, Rain, Thunderstorm, Snow, Fog, Night).
   - Instant °C / °F unit toggle.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (or Python 3.14)
- Virtual environment (`venv`)

### 2. Installation
```bash
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 📂 Project Architecture
```
weather forecasting/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── weather_forecast_ai/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── forecast/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── ai_engine.py         # ML pipeline & HistGradientBoostingClassifier
    ├── weather_service.py   # Open-Meteo APIs & recommendation generator
    ├── tests.py
    ├── ml_models/           # Serialized joblib models
    ├── templates/
    │   └── index.html       # Glassmorphic dashboard UI
    └── static/
        ├── css/
        │   └── style.css    # Premium glassmorphism design system
        └── js/
            └── main.js      # Chart.js, SVG gauge, unit switcher, search
```
