/**
 * SYNOPTIC Weather Background Notification Service Worker
 * Handles background push alerts and system notification clicks.
 */

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

// Handle incoming background push notifications
self.addEventListener('push', (event) => {
    let data = {
        title: 'SYNOPTIC Weather Alert',
        body: 'Significant atmospheric change detected.',
        icon: '/static/icons/weather-alert.png',
        tag: 'synoptic-weather-alert',
        vibrate: [200, 100, 200]
    };

    if (event.data) {
        try {
            data = Object.assign(data, event.data.json());
        } catch (e) {
            data.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: data.icon,
            badge: data.icon,
            tag: data.tag,
            vibrate: data.vibrate || [200, 100, 200],
            data: { url: data.url || '/' }
        })
    );
});

// Focus or open weather tab on notification click
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const targetUrl = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            for (const client of clientList) {
                if (client.url.includes(self.registration.scope) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
