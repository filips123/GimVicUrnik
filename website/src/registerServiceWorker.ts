import { registerSW } from 'virtual:pwa-register'
import type { Router } from 'vue-router'

import { useSnackbarStore } from '@/composables/snackbar'

export default function registerServiceWorker(router: Router) {
  const searchParams = new URLSearchParams(location.search)
  let immediatelyUpdate = false

  if (searchParams.has('update')) {
    // Display a message while updating the service worker
    const { displaySnackbar } = useSnackbarStore()
    displaySnackbar('Posodabljanje ...')

    // Mark that we need to update the service worker
    immediatelyUpdate = true
  }

  if (searchParams.has('updating')) {
    // Display a success message if the app was updated
    const { displaySnackbar } = useSnackbarStore()
    displaySnackbar('Aplikacija posodobljena')

    // Hide the parameter after the app was updated
    router.replace(location.pathname)
  }

  setTimeout(() => {
    if (searchParams.has('update') || searchParams.has('updating')) {
      // Hide the parameter if the app was already up to date
      router.replace(location.pathname)
    }
  }, 4000)

  const updateSW = registerSW({
    immediate: true,

    onRegisteredSW(swUrl, registration) {
      if (!registration) return

      // Routinely check for app updates by testing for a new service worker
      setInterval(() => registration.update().catch(() => {}), 60 * 60 * 1000)
    },

    onNeedRefresh() {
      if (immediatelyUpdate) {
        console.log('Update parameter detected, updating the service worker...')

        // Update the service worker immediately if requested
        performUpdate()
      } else {
        console.log('New content is available, prompting the user to refresh...')

        // Prompt the user to update the service worker
        const { displaySnackbar } = useSnackbarStore()
        displaySnackbar('Na voljo je posodobitev', 'Posodobi', performUpdate, -1)
      }
    },
  })

  const performUpdate = async () => {
    // Display a message while updating the service worker
    const { displaySnackbar } = useSnackbarStore()
    displaySnackbar('Posodabljanje ...')

    // Add query parameter so we know the app was updated
    history.replaceState(history.state, '', location.pathname + '?updating=1')

    // Update the service worker
    await updateSW()
  }
}
