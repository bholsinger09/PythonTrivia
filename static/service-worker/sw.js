/**
 * Service Worker for Python Trivia PWA
 * Provides offline functionality, caching, and background sync
 */

const CACHE_NAME = 'python-trivia-v1.0.0';
const OFFLINE_CACHE = 'python-trivia-offline-v1';

// Assets to cache for offline functionality
const CACHE_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/js/game.js',
  '/static/manifest.json',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
  // Core pages
  '/game',
  '/categories',
  '/difficulty',
  '/leaderboard'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  /\/api\/questions/,
  /\/api\/game_session/,
  /\/api\/categories/,
  /\/api\/difficulties/
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('🚀 Service Worker installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache essential assets
      caches.open(CACHE_NAME).then((cache) => {
        console.log('📦 Caching essential assets...');
        return cache.addAll(CACHE_ASSETS).catch((error) => {
          console.warn('⚠️ Some assets failed to cache:', error);
          // Don't fail the entire installation if some assets can't be cached
        });
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activating...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== OFFLINE_CACHE) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Claim all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - handle all network requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests
  if (isAPIRequest(request.url)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isAssetRequest(request.url)) {
    event.respondWith(handleAssetRequest(request));
  } else {
    event.respondWith(handlePageRequest(request));
  }
});

// Handle API requests with network-first strategy
async function handleAPIRequest(request) {
  try {
    // Try network first
    const response = await fetch(request);
    
    if (response.ok) {
      // Cache successful responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
      return response;
    }
    
    throw new Error(`Network response not ok: ${response.status}`);
  } catch (error) {
    console.log('🔄 API request failed, trying cache:', request.url);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for specific endpoints
    return createOfflineResponse(request);
  }
}

// Handle asset requests with cache-first strategy
async function handleAssetRequest(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Return from cache immediately
    return cachedResponse;
  }
  
  try {
    // Fetch and cache new assets
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('❌ Asset request failed:', request.url);
    return new Response('Asset not available offline', { status: 404 });
  }
}

// Handle page requests with cache-first, then network
async function handlePageRequest(request) {
  try {
    // Try cache first for faster loading
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Update cache in background
      fetch(request).then((response) => {
        if (response.ok) {
          const cache = caches.open(CACHE_NAME);
          cache.then(c => c.put(request, response));
        }
      }).catch(() => {}); // Silent fail for background updates
      
      return cachedResponse;
    }
    
    // Fallback to network
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.log('📄 Page request failed, returning offline page:', request.url);
    return createOfflinePage();
  }
}

// Helper functions
function isAPIRequest(url) {
  return url.includes('/api/') || API_CACHE_PATTERNS.some(pattern => pattern.test(url));
}

function isAssetRequest(url) {
  return url.includes('/static/') || 
         url.includes('.css') || 
         url.includes('.js') || 
         url.includes('.png') || 
         url.includes('.jpg') || 
         url.includes('.svg') ||
         url.includes('fonts.googleapis.com');
}

function createOfflineResponse(request) {
  // Return appropriate offline responses for different API endpoints
  if (request.url.includes('/api/questions')) {
    return new Response(JSON.stringify({
      questions: [],
      message: 'Offline mode - no new questions available'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
  
  return new Response(JSON.stringify({
    error: 'Offline',
    message: 'This feature is not available offline'
  }), {
    status: 503,
    headers: { 'Content-Type': 'application/json' }
  });
}

function createOfflinePage() {
  const offlineHTML = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Offline - Python Trivia</title>
      <style>
        body {
          font-family: 'Inter', sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          margin: 0;
          text-align: center;
          padding: 20px;
        }
        .offline-container {
          max-width: 400px;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 20px;
          padding: 40px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        .offline-icon {
          font-size: 4rem;
          margin-bottom: 20px;
        }
        h1 {
          margin-bottom: 20px;
          font-size: 2rem;
        }
        p {
          margin-bottom: 30px;
          opacity: 0.8;
        }
        .btn {
          background: #4f46e5;
          color: white;
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          text-decoration: none;
          display: inline-block;
          transition: all 0.3s ease;
        }
        .btn:hover {
          background: #4338ca;
          transform: translateY(-2px);
        }
      </style>
    </head>
    <body>
      <div class="offline-container">
        <div class="offline-icon">🐍</div>
        <h1>You're Offline</h1>
        <p>Don't worry! You can still access cached content and play previously loaded games.</p>
        <a href="/" class="btn" onclick="window.location.reload()">Try Again</a>
      </div>
    </body>
    </html>
  `;
  
  return new Response(offlineHTML, {
    headers: { 'Content-Type': 'text/html' }
  });
}

// Background sync for when connection is restored
self.addEventListener('sync', (event) => {
  if (event.tag === 'game-data-sync') {
    event.waitUntil(syncGameData());
  }
});

async function syncGameData() {
  console.log('🔄 Syncing game data...');
  // Implement game data synchronization when online
  try {
    // This would sync any cached game progress or scores
    const cache = await caches.open(OFFLINE_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('game-progress')) {
        // Sync game progress data
        const response = await cache.match(request);
        const data = await response.json();
        
        // Send to server when online
        await fetch('/api/sync-progress', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        // Remove from offline cache after successful sync
        await cache.delete(request);
      }
    }
    
    console.log('✅ Game data sync completed');
  } catch (error) {
    console.error('❌ Game data sync failed:', error);
  }
}

// Push notifications for re-engagement
self.addEventListener('push', (event) => {
  const options = {
    body: event.data ? event.data.text() : 'New trivia questions available!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-96x96.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/game'
    },
    actions: [
      {
        action: 'play',
        title: 'Play Now',
        icon: '/static/icons/icon-96x96.png'
      },
      {
        action: 'dismiss',
        title: 'Later'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Python Trivia', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'play') {
    event.waitUntil(
      clients.openWindow('/game')
    );
  } else if (!event.action) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});