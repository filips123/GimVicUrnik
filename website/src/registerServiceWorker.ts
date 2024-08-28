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
    immediatelyUpdate = true
  }

  if (searchParams.has('updating')) {
    // Display a success message if the app was updated
    const { displaySnackbar } = useSnackbarStore()
    displaySnackbar('Aplikacija posodobljena')
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
      setInterval(() => registration.update(), 60 * 60 * 1000)
    },

    onNeedRefresh() {
      if (immediatelyUpdate) {
        // Update the service worker immediately if requested
        console.log('Update parameter detected, updating the service worker...')
        performUpdate()
      } else {
        // Prompt the user to update the service worker
        console.log('New content is available, prompting the user to refresh...')
        const { displaySnackbar } = useSnackbarStore()
        displaySnackbar('Na voljo je posodobitev', 'Posodobi', performUpdate, -1)
      }
    },
  })

  const performUpdate = async () => {
    await router.replace({ path: location.pathname, query: { updating: 1 } })
    await updateSW()
  }
}
