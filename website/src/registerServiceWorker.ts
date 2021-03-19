/* eslint-disable no-console */

import { register } from 'register-service-worker'

// TODO: Fix service worker to also serve offline page for any request

if (process.env.NODE_ENV === 'production') {
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready () {
      console.log('App is being served from cache by a service worker.\nFor more details, visit https://goo.gl/AFskqB')
    },
    registered (registration) {
      console.log('Service worker has been registered.')

      // Routinely check for app updates by testing for a new service worker
      setInterval(() => { registration.update() }, 1000 * 60 * 60)
    },
    cached () {
      console.log('Content has been cached for offline use.')
    },
    updatefound () {
      console.log('New content is downloading.')
    },
    updated (registration) {
      console.log('New content is available; please refresh.')

      // Dispatch update event so the app can display a message to the user
      document.dispatchEvent(new CustomEvent('serviceWorkerUpdated', { detail: registration }))
    },
    offline () {
      console.log('No internet connection found. App is running in offline mode.')

      // Dispatch offline event so the app can display a message to the user
      document.dispatchEvent(new CustomEvent('serviceWorkerOffline'))
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })
}
