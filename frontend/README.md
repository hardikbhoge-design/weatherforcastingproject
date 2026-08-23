# 🎨 Frontend Presentation Layer

This directory contains all client-side code, markup, styles, scripts, and media assets for the **AI Weather Forecasting & Advisory System**.

---

## 📂 Structure

```
frontend/
├── templates/
│   ├── index.html       # Glassmorphic weather dashboard with SVG gauges & Chart.js
│   └── login.html       # Authentication portal (Login, Register & Guest Mode)
└── static/
    ├── css/
    │   ├── style.css    # Core design system (glassmorphism tokens, flex/grid, weather animations)
    │   ├── synoptic.css # Enhanced synoptic weather station card styles & responsive layout
    │   └── auth.css     # Premium split-screen glassmorphic authentication styling
    ├── js/
    │   ├── main.js      # Core client logic, Chart.js graphs, speech synthesis, geolocation
    │   ├── auth.js      # Tab switching, client-side validation, password toggles
    │   └── sw.js        # Progressive Web App (PWA) offline Service Worker
    └── img/
        └── edge_lake_bg.jpg # High-resolution dynamic landscape background
```

---

## 🌟 Key Features
- **Modern Glassmorphic Design:** Translucent backdrop blur, gradient borders, and reactive atmospheric lighting.
- **Chart.js 4.4 Visuals:** 24-hour dual-axis hourly temperature and precipitation graphs.
- **Bilingual Voice Alerts:** Web Speech API TTS synthesis in English and Hinglish.
- **Progressive Web App (PWA):** Offline asset caching and standalone installability via Service Worker (`sw.js`).
