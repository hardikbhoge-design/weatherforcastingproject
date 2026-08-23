# ⚙️ Backend Application & Machine Learning Layer

This directory contains the entire server-side application logic, REST API routing, meteorological data fetching services, and Scikit-Learn machine learning pipeline.

---

## 📂 Structure

```
backend/
├── weather_forecast_ai/
│   ├── settings.py      # Django global project settings, middleware, databases & static paths
│   ├── urls.py          # Root URL dispatcher
│   ├── wsgi.py          # WSGI entrypoint for production servers (Gunicorn/uWSGI)
│   └── asgi.py          # ASGI entrypoint for asynchronous event handling
├── forecast/
│   ├── ai_engine.py     # HistGradientBoostingClassifier ML engine, TimeSeriesSplit & Joblib cache
│   ├── weather_service.py # Open-Meteo API consumer, WMO decoders, geocoding & recommendations
│   ├── views.py         # HTTP view controllers and JSON REST endpoints
│   ├── models.py        # Django ORM data models (Search History & Favorite Cities)
│   ├── urls.py          # Sub-routing for dashboard, auth, APIs, and Service Worker
│   ├── admin.py         # Django Admin dashboard registrations
│   ├── apps.py          # AppConfig definition
│   ├── tests.py         # Unit & integration test suites
│   └── ml_models/       # Serialized .joblib trained machine learning models
├── manage.py            # Django command-line administrative utility
└── requirements.txt     # Python dependencies and versions
```

---

## 🧠 Machine Learning Engine (`ai_engine.py`)
- **Algorithm:** `HistGradientBoostingClassifier(class_weight='balanced')`
- **Validation:** `TimeSeriesSplit(n_splits=3)`
- **Concurrency:** Process/thread-safe caching with `filelock.FileLock` and `joblib.dump/load`
- **Features Analyzed:** 16 thermodynamic, trend, and cyclical solar harmonic features
