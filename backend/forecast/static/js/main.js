/**
 * OBSIDIAN WEATHER DASHBOARD - Interactive Controller
 * Features:
 * 1. Real-time Live Ticking Clock (Synchronized with local/searched timezone)
 * 2. Interactive Range Tabs: Today, Tomorrow, Next 7 Days (Ultra-reliable switching)
 * 3. User Observer Profile Modal & Account Status
 * 4. Leaflet Dark World Map with high-visibility city pins and 100% synced temperatures
 * 5. Map & Navbar Fast Search with FlyTo Animation
 * 6. 1-Click GPS Location Auto-Detection
 * 7. Web Speech API Bilingual Audio (English/Hinglish)
 * 8. Background Push Notifications (Service Worker)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Parse Embedded Weather Data
    let weatherData = null;
    try {
        const rawJsonEl = document.getElementById('weather-raw-data');
        if (rawJsonEl && rawJsonEl.textContent) {
            weatherData = JSON.parse(rawJsonEl.textContent);
        }
    } catch (e) {
        console.error('Error parsing weather raw data:', e);
    }

    // 2. Real-Time Live Ticking Clock
    const initLiveTickingClock = () => {
        const clockEl = document.getElementById('syn-live-datetime');
        if (!clockEl) return;

        const updateClock = () => {
            const now = new Date();
            const timezone = weatherData?.location?.timezone;
            
            try {
                const timeFormatter = new Intl.DateTimeFormat('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true,
                    timeZone: (timezone && timezone !== 'auto') ? timezone : undefined
                });
                clockEl.textContent = timeFormatter.format(now);
            } catch (e) {
                clockEl.textContent = now.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit', hour12: true });
            }
        };

        updateClock();
        setInterval(updateClock, 1000);
    };

    // 3. Unit Switcher (°C <=> °F)
    let currentUnit = 'C';
    const setupUnitSwitcher = () => {
        const toggleBtn = document.getElementById('syn-unit-toggle');
        if (!toggleBtn) return;

        toggleBtn.addEventListener('click', () => {
            currentUnit = (currentUnit === 'C') ? 'F' : 'C';
            toggleBtn.innerHTML = currentUnit === 'C' ? '<i class="fa-solid fa-moon"></i>' : '<i class="fa-solid fa-sun text-gold"></i>';
            updateAllTemperatures();
        });
    };

    const updateAllTemperatures = () => {
        document.querySelectorAll('.syn-temp-dyn, #syn-hero-temp, #syn-hero-feels').forEach(el => {
            const tempC = parseFloat(el.getAttribute('data-temp-c'));
            if (!isNaN(tempC)) {
                if (currentUnit === 'C') {
                    el.textContent = `${Math.round(tempC)}°`;
                } else {
                    const tempF = (tempC * 9/5) + 32;
                    el.textContent = `${Math.round(tempF)}°`;
                }
            }
        });
    };

    // 4. Interactive Range Tabs (Today | Tomorrow | Next 7 Days)
    const setupRangeTabs = () => {
        const tabBtns = document.querySelectorAll('.obs-tab-text');
        const tabToday = document.getElementById('obs-tab-today');
        const tabTomorrow = document.getElementById('obs-tab-tomorrow');
        const tab7Days = document.getElementById('obs-tab-7days');
        const cardsStrip = document.getElementById('obs-forecast-cards-container');
        const aqiView = document.getElementById('obs-aqi-view');
        const forecastModeBtn = document.getElementById('toggle-forecast-mode');
        const aqiModeBtn = document.getElementById('toggle-aqi-mode');

        const switchTab = (rangeName) => {
            tabBtns.forEach(b => {
                if (b.getAttribute('data-range') === rangeName) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });

            // Ensure we are in Forecast mode
            if (forecastModeBtn && aqiModeBtn) {
                forecastModeBtn.classList.add('active');
                aqiModeBtn.classList.remove('active');
                if (cardsStrip) cardsStrip.style.display = 'block';
                if (aqiView) aqiView.style.display = 'none';
            }

            if (rangeName === 'today') {
                if (tabToday) tabToday.style.display = 'block';
                if (tabTomorrow) tabTomorrow.style.display = 'none';
                if (tab7Days) tab7Days.style.display = 'none';
            } else if (rangeName === 'tomorrow') {
                if (tabToday) tabToday.style.display = 'none';
                if (tabTomorrow) tabTomorrow.style.display = 'block';
                if (tab7Days) tab7Days.style.display = 'none';
            } else if (rangeName === '7days') {
                if (tabToday) tabToday.style.display = 'none';
                if (tabTomorrow) tabTomorrow.style.display = 'none';
                if (tab7Days) tab7Days.style.display = 'block';
            }
        };

        tabBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const range = btn.getAttribute('data-range') || 'today';
                switchTab(range);
            });
        });

        // Direct ID bindings as fail-safe
        document.getElementById('tab-btn-today')?.addEventListener('click', () => switchTab('today'));
        document.getElementById('tab-btn-tomorrow')?.addEventListener('click', () => switchTab('tomorrow'));
        document.getElementById('tab-btn-7days')?.addEventListener('click', () => switchTab('7days'));
    };

    // 5. Forecast vs Air Quality Toggle Mode
    const setupModeToggle = () => {
        const forecastBtn = document.getElementById('toggle-forecast-mode');
        const aqiBtn = document.getElementById('toggle-aqi-mode');
        const cardsStrip = document.getElementById('obs-forecast-cards-container');
        const aqiView = document.getElementById('obs-aqi-view');

        if (!forecastBtn || !aqiBtn) return;

        forecastBtn.addEventListener('click', (e) => {
            e.preventDefault();
            forecastBtn.classList.add('active');
            aqiBtn.classList.remove('active');
            if (cardsStrip) cardsStrip.style.display = 'block';
            if (aqiView) aqiView.style.display = 'none';
        });

        aqiBtn.addEventListener('click', (e) => {
            e.preventDefault();
            aqiBtn.classList.add('active');
            forecastBtn.classList.remove('active');
            if (cardsStrip) cardsStrip.style.display = 'none';
            if (aqiView) aqiView.style.display = 'block';
        });
    };

    // 6. Leaflet Interactive Dark World Map Initialization
    let leafletMap = null;
    const initGlobalLeafletMap = () => {
        const mapContainer = document.getElementById('obs-global-leaflet-map');
        if (!mapContainer || typeof L === 'undefined') return;

        const currentLat = weatherData?.location?.latitude || 51.5074;
        const currentLon = weatherData?.location?.longitude || -0.1278;
        const currentCity = weatherData?.location?.city || 'London';
        const currentTemp = Math.round(weatherData?.current?.temperature || 15);

        // Initialize map centered around the active searched/GPS city
        leafletMap = L.map('obs-global-leaflet-map', {
            center: [currentLat, currentLon],
            zoom: 5,
            zoomControl: false,
            attributionControl: false
        });

        // High-clarity CartoDB Dark Matter with labels
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd',
        }).addTo(leafletMap);

        // Comprehensive Global & Indian City Pins
        const benchmarkCities = [
            { name: 'Nagpur', lat: 21.1458, lon: 79.0882, temp: '32°' },
            { name: 'Mumbai', lat: 19.0760, lon: 72.8777, temp: '28°' },
            { name: 'Delhi', lat: 28.6139, lon: 77.2090, temp: '34°' },
            { name: 'Bangalore', lat: 12.9716, lon: 77.5946, temp: '26°' },
            { name: 'Pune', lat: 18.5204, lon: 73.8567, temp: '27°' },
            { name: 'London', lat: 51.5074, lon: -0.1278, temp: '16°' },
            { name: 'San Francisco', lat: 37.7749, lon: -122.4194, temp: '14°' },
            { name: 'California', lat: 36.7783, lon: -119.4179, temp: '29°' },
            { name: 'Beijing', lat: 39.9042, lon: 116.4074, temp: '19°' },
            { name: 'Jerusalem', lat: 31.7683, lon: 35.2137, temp: '31°' },
            { name: 'Tokyo', lat: 35.6762, lon: 139.6503, temp: '24°' },
            { name: 'Sydney', lat: -33.8688, lon: 151.2093, temp: '21°' }
        ];

        // Ensure active current searched city has the 100% exact temperature matching the hero card
        let cityPins = [];
        let matchedActive = false;

        benchmarkCities.forEach(c => {
            if (c.name.toLowerCase() === currentCity.toLowerCase()) {
                cityPins.push({ name: currentCity, lat: currentLat, lon: currentLon, temp: `${currentTemp}°`, isCurrent: true });
                matchedActive = true;
            } else {
                cityPins.push(c);
            }
        });

        if (!matchedActive) {
            cityPins.unshift({ name: currentCity, lat: currentLat, lon: currentLon, temp: `${currentTemp}°`, isCurrent: true });
        }

        // Render all map pins
        cityPins.forEach(pin => {
            const isCurrent = !!pin.isCurrent;
            const markerHtml = `
                <div class="obs-custom-map-marker ${isCurrent ? 'active-pin' : ''}">
                    <i class="fa-solid ${isCurrent ? 'fa-location-dot text-cyan' : 'fa-circle-dot'}"></i>
                    <span>${pin.name} <strong>${pin.temp}</strong></span>
                </div>
            `;
            const customIcon = L.divIcon({
                html: markerHtml,
                className: 'obs-map-div-icon',
                iconSize: [120, 34],
                iconAnchor: [60, 17]
            });

            const marker = L.marker([pin.lat, pin.lon], { icon: customIcon }).addTo(leafletMap);
            marker.on('click', () => {
                window.location.href = `/?city=${encodeURIComponent(pin.name)}&guest=1`;
            });
        });

        // Smoothly fly to current active city on map
        setTimeout(() => {
            leafletMap.flyTo([currentLat, currentLon], 5, { duration: 1.4 });
        }, 300);

        // Map Control Buttons
        document.getElementById('obs-map-zoom-in')?.addEventListener('click', () => leafletMap.zoomIn());
        document.getElementById('obs-map-zoom-out')?.addEventListener('click', () => leafletMap.zoomOut());
        document.getElementById('geo-location-btn')?.addEventListener('click', () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(pos => {
                    leafletMap.flyTo([pos.coords.latitude, pos.coords.longitude], 6, { duration: 1.2 });
                });
            }
        });

        document.getElementById('obs-explore-map-btn')?.addEventListener('click', () => {
            document.getElementById('open-radar-btn')?.click();
        });

        // Map Search Handler
        const mapSearchInput = document.getElementById('obs-map-search-input');
        const mapSearchResults = document.getElementById('obs-map-search-results');
        let mapSearchDebounce = null;

        if (mapSearchInput && mapSearchResults) {
            mapSearchInput.addEventListener('input', (e) => {
                const q = e.target.value.trim();
                clearTimeout(mapSearchDebounce);
                if (q.length < 2) {
                    mapSearchResults.style.display = 'none';
                    return;
                }

                mapSearchDebounce = setTimeout(() => {
                    fetch(`/api/search-cities/?q=${encodeURIComponent(q)}`)
                        .then(res => res.json())
                        .then(data => {
                            if (data.results && data.results.length > 0) {
                                mapSearchResults.innerHTML = data.results.map(item => `
                                    <div class="obs-suggestion-item" data-city="${item.name}">
                                        <i class="fa-solid fa-location-dot text-cyan"></i>
                                        <span><strong>${item.name}</strong>, ${item.country || ''}</span>
                                    </div>
                                `).join('');
                                mapSearchResults.style.display = 'block';

                                mapSearchResults.querySelectorAll('.obs-suggestion-item').forEach(el => {
                                    el.addEventListener('click', () => {
                                        const city = el.getAttribute('data-city');
                                        window.location.href = `/?city=${encodeURIComponent(city)}&guest=1`;
                                    });
                                });
                            } else {
                                mapSearchResults.style.display = 'none';
                            }
                        })
                        .catch(() => { mapSearchResults.style.display = 'none'; });
                }, 200);
            });

            mapSearchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const q = mapSearchInput.value.trim();
                    if (q) {
                        window.location.href = `/?city=${encodeURIComponent(q)}&guest=1`;
                    }
                }
            });

            document.addEventListener('click', (e) => {
                if (!mapSearchInput.contains(e.target) && !mapSearchResults.contains(e.target)) {
                    mapSearchResults.style.display = 'none';
                }
            });
        }

        // Quick Jump Buttons
        document.querySelectorAll('.obs-map-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const city = btn.getAttribute('data-city');
                if (city) {
                    window.location.href = `/?city=${encodeURIComponent(city)}&guest=1`;
                }
            });
        });
    };

    // 7. Instant Real GPS Geolocation & Navbar Search Autocomplete
    const setupSearchAndLocation = () => {
        const searchInput = document.getElementById('syn-search-input');
        const suggestionsBox = document.getElementById('syn-suggestions-box');
        const locationPillBtn = document.getElementById('open-search-btn');
        let debounceTimer = null;

        // 1-Click Real GPS Location Detector
        locationPillBtn?.addEventListener('click', () => {
            if (navigator.geolocation) {
                const originalHtml = locationPillBtn.innerHTML;
                locationPillBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-cyan"></i> <span>Detecting GPS Location...</span>';
                
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        const lat = pos.coords.latitude.toFixed(4);
                        const lon = pos.coords.longitude.toFixed(4);
                        window.location.href = `/?lat=${lat}&lon=${lon}&guest=1`;
                    },
                    (err) => {
                        locationPillBtn.innerHTML = originalHtml;
                        alert('Could not access your GPS coordinates. Please ensure browser location permissions are enabled, or search for your city directly in the search bar.');
                    },
                    { timeout: 10000, enableHighAccuracy: true }
                );
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        });

        if (!searchInput || !suggestionsBox) return;

        // Autocomplete typing handler
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.trim();
            clearTimeout(debounceTimer);
            if (q.length < 2) {
                suggestionsBox.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search-cities/?q=${encodeURIComponent(q)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.results && data.results.length > 0) {
                            suggestionsBox.innerHTML = data.results.map(item => `
                                <div class="obs-suggestion-item" data-city="${item.name}">
                                    <i class="fa-solid fa-location-dot text-cyan"></i>
                                    <span><strong>${item.name}</strong>, ${item.country || ''}</span>
                                </div>
                            `).join('');
                            suggestionsBox.style.display = 'block';

                            suggestionsBox.querySelectorAll('.obs-suggestion-item').forEach(el => {
                                el.addEventListener('click', () => {
                                    const city = el.getAttribute('data-city');
                                    window.location.href = `/?city=${encodeURIComponent(city)}&guest=1`;
                                });
                            });
                        } else {
                            suggestionsBox.style.display = 'none';
                        }
                    })
                    .catch(() => { suggestionsBox.style.display = 'none'; });
            }, 200);
        });

        // Enter key in search box
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const q = searchInput.value.trim();
                if (q) {
                    window.location.href = `/?city=${encodeURIComponent(q)}&guest=1`;
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.style.display = 'none';
            }
        });
    };

    // 8. Sliding Menu Drawer & Modals Setup (Including Profile Modal)
    const setupModals = () => {
        // Drawer
        const openMenuBtn = document.getElementById('open-menu-btn');
        const closeMenuBtn = document.getElementById('close-menu-btn');
        const drawerOverlay = document.getElementById('menu-drawer-overlay');

        openMenuBtn?.addEventListener('click', () => drawerOverlay?.classList.add('active'));
        closeMenuBtn?.addEventListener('click', () => drawerOverlay?.classList.remove('active'));

        // Observer Profile Modal
        const openProfileBtn = document.getElementById('open-profile-btn');
        const closeProfileBtn = document.getElementById('close-profile-btn');
        const profileOverlay = document.getElementById('profile-modal-overlay');

        const openProfile = () => {
            drawerOverlay?.classList.remove('active');
            profileOverlay?.classList.add('active');
        };

        openProfileBtn?.addEventListener('click', openProfile);
        closeProfileBtn?.addEventListener('click', () => profileOverlay?.classList.remove('active'));

        // Risk & Decision Assistant Modal
        const openInsightsBtn = document.getElementById('open-insights-btn');
        const openAssistantBtn = document.getElementById('open-assistant-btn');
        const openRiskModalBtn = document.getElementById('open-risk-modal-btn');
        const openFogModalBtn = document.getElementById('open-fog-modal-btn');
        const drawerInsightsBtn = document.getElementById('drawer-insights-btn');
        const closeInsightsBtn = document.getElementById('close-insights-btn');
        const insightsOverlay = document.getElementById('insights-modal-overlay');

        const openInsights = () => {
            drawerOverlay?.classList.remove('active');
            insightsOverlay?.classList.add('active');
        };

        [openInsightsBtn, openAssistantBtn, openRiskModalBtn, openFogModalBtn, drawerInsightsBtn].forEach(btn => {
            btn?.addEventListener('click', openInsights);
        });
        closeInsightsBtn?.addEventListener('click', () => insightsOverlay?.classList.remove('active'));

        // Radar 24H AI Chart Modal
        const openRadarBtn = document.getElementById('open-radar-btn');
        const drawerRadarBtn = document.getElementById('drawer-radar-btn');
        const closeRadarBtn = document.getElementById('close-radar-btn');
        const radarOverlay = document.getElementById('radar-modal-overlay');

        const openRadar = () => {
            drawerOverlay?.classList.remove('active');
            radarOverlay?.classList.add('active');
            setTimeout(render24HChart, 150);
        };

        openRadarBtn?.addEventListener('click', openRadar);
        drawerRadarBtn?.addEventListener('click', openRadar);
        closeRadarBtn?.addEventListener('click', () => radarOverlay?.classList.remove('active'));

        // Push Notifications Modal
        const openNotifBtn = document.getElementById('open-notif-btn');
        const drawerNotifBtn = document.getElementById('drawer-notif-btn');
        const closeNotifBtn = document.getElementById('close-notif-btn');
        const notifOverlay = document.getElementById('notif-modal-overlay');

        const openNotif = () => {
            drawerOverlay?.classList.remove('active');
            notifOverlay?.classList.add('active');
        };

        openNotifBtn?.addEventListener('click', openNotif);
        drawerNotifBtn?.addEventListener('click', openNotif);
        closeNotifBtn?.addEventListener('click', () => notifOverlay?.classList.remove('active'));

        // Overlay click outside to close
        [drawerOverlay, profileOverlay, insightsOverlay, radarOverlay, notifOverlay].forEach(overlay => {
            overlay?.addEventListener('click', (e) => {
                if (e.target === overlay) overlay.classList.remove('active');
            });
        });
    };

    // 9. Render 24-Hour AI Interactive Radar Chart
    let chartInstance = null;
    const render24HChart = () => {
        const ctx = document.getElementById('synHourlyChart')?.getContext('2d');
        if (!ctx || !weatherData || !weatherData.hourly) return;

        const labels = weatherData.hourly.map(h => h.time);
        const temps = weatherData.hourly.map(h => h.temp);
        const precipProbs = weatherData.hourly.map(h => h.precip_prob);

        if (chartInstance) chartInstance.destroy();

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: temps,
                        borderColor: '#facc15',
                        backgroundColor: 'rgba(250, 204, 21, 0.12)',
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Rain Chance (%)',
                        data: precipProbs,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.15)',
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#ffffff', font: { family: 'Plus Jakarta Sans' } } }
                },
                scales: {
                    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.06)' } },
                    y: { type: 'linear', position: 'left', ticks: { color: '#facc15' }, grid: { color: 'rgba(255,255,255,0.06)' } },
                    y1: { type: 'linear', position: 'right', min: 0, max: 100, ticks: { color: '#38bdf8' }, grid: { drawOnChartArea: false } }
                }
            }
        });
    };

    // 10. Web Speech API Voice Alerts (English & Hinglish)
    const setupVoiceBroadcast = () => {
        const playBtn = document.getElementById('syn-voice-play-btn');
        const langBtns = document.querySelectorAll('.syn-voice-lang-btn');
        let selectedLang = 'en';

        langBtns.forEach(b => {
            b.addEventListener('click', (e) => {
                e.stopPropagation();
                langBtns.forEach(btn => btn.classList.remove('active'));
                b.classList.add('active');
                selectedLang = b.getAttribute('data-lang');
            });
        });

        if (!playBtn || !('speechSynthesis' in window)) return;

        playBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                return;
            }

            const voiceObj = weatherData?.enhancements?.voice;
            const textToSpeak = (selectedLang === 'hinglish' && voiceObj?.hinglish) ? voiceObj.hinglish : (voiceObj?.en || 'Real-time meteorological forecast ready.');

            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        });
    };

    // 11. Service Worker & Background Push Notifications
    const setupBackgroundPush = () => {
        const masterToggle = document.getElementById('master-notif-toggle');
        const testBtn = document.getElementById('test-notif-btn');

        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(err => console.log('SW registration note:', err));
        }

        masterToggle?.addEventListener('change', async () => {
            if (masterToggle.checked && 'Notification' in window) {
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    masterToggle.checked = false;
                    alert('Please allow notification permissions in your browser settings.');
                }
            }
        });

        testBtn?.addEventListener('click', () => {
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🌧️ Rain Approaching Alert', {
                    body: 'Rain probability increased to 75%. Carry an umbrella!',
                    icon: '/static/icons/umbrella.png'
                });
            } else {
                alert('Enable background notification toggle first!');
            }
        });
    };

    // Initialize all components
    initLiveTickingClock();
    setupUnitSwitcher();
    setupRangeTabs();
    setupModeToggle();
    setupSearchAndLocation();
    setupModals();
    setupVoiceBroadcast();
    setupBackgroundPush();
    initGlobalLeafletMap();
});
