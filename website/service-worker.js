function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

const mainCacheName = 'gimvic-timetable-main'
const dataCacheName = 'gimvic-timetable-data'

const offlinePage = '/'
const offlineData = '/js/data.js'
const offlineAssets = [
  '/css/bootstrap.min.css',
  '/css/timetable.css',
  '/js/bootstrap.min.js',
  '/js/jquery.min.js',
  '/js/navigo.min.js',
  '/js/pulltorefresh.min.js',
  '/js/broadcastchannel.min.js',
  '/js/timetable.js',
  '/icons/circle-badge-192x192.png'
]

addEventListener('install', async (event) => {
  event.waitUntil(self.skipWaiting())

  event.waitUntil(async function () {
    const mainCache = await caches.open(mainCacheName)
    await mainCache.addAll([offlinePage, ...offlineAssets])

    const dataCache = await caches.open(dataCacheName)
    await dataCache.addAll([offlineData])

    const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
    cacheUpdatesChannel.postMessage({date: new Date()})
  }())
})

self.addEventListener('activate', async (event) => {
  event.waitUntil(self.clients.claim())
});

addEventListener('fetch', async (event) => {
  const { request } = event

  if (request.headers.has('range')) return
  if (request.method !== 'GET') return

  event.respondWith(async function () {
    const cachedResponse = await caches.match(request)
    if (cachedResponse) return cachedResponse

    try {
      return await fetch(request)
    } catch (err) {
      if (request.mode === 'navigate') {
        return caches.match(offlinePage)
      }

      throw err
    }
  }())

  event.waitUntil(async function () {
    const cachedResponse = await caches.match(request)
    if (!cachedResponse) return

    const networkResponse = await fetch(request)

    if (request.url.includes(offlineData)) {
      const dataCache = await caches.open(dataCacheName)
      await dataCache.put(request, networkResponse)

      await sleep(100)
      const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
      cacheUpdatesChannel.postMessage({date: new Date()})

    } else {
      const mainCache = await caches.open(mainCacheName)
      await mainCache.put(request, networkResponse)
    }
  }())
})

self.onmessage = async (event) => {
  const action = event.data.action

  if (action === 'clear-cache-all') {
    await caches.delete(mainCacheName)
    await caches.delete(dataCacheName)

    const mainCache = await caches.open(mainCacheName)
    await mainCache.addAll([offlinePage, ...offlineAssets])

    const dataCache = await caches.open(dataCacheName)
    await dataCache.addAll([offlineData])

    await sleep(100)
    const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
    cacheUpdatesChannel.postMessage({date: new Date(), refreshAll: true})
  }

  if (action === 'clear-cache-data') {
    await caches.delete(dataCacheName)

    const dataCache = await caches.open(dataCacheName)
    await dataCache.addAll([offlineData])

    await sleep(100)
    const cacheUpdatesChannel = new BroadcastChannel('cache-updates')
    cacheUpdatesChannel.postMessage({date: new Date(), refreshData: true})
  }
}
