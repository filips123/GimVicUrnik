import { captureException } from '@sentry/browser'
import { storeToRefs } from 'pinia'

import { useSnackbarStore } from '@/composables/snackbar'
import { useDocumentsStore } from '@/stores/documents'
import { useFoodStore } from '@/stores/food'
import { useListsStore } from '@/stores/lists'
import { useSettingsStore } from '@/stores/settings'
import { useTimetableStore } from '@/stores/timetable'

export async function updateAllData(showSuccess: boolean = true): Promise<void> {
  const documentsStore = useDocumentsStore()
  const foodStore = useFoodStore()
  const timetableStore = useTimetableStore()
  const listsStore = useListsStore()

  const { displaySnackbar } = useSnackbarStore()

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  if (showSuccess) {
    displaySnackbar('Posodabljanje ...')
  }

  await Promise.all([
    documentsStore.updateDocuments(),
    foodStore.updateMenus(),
    foodStore.updateLunchSchedules(),
    timetableStore.updateTimetable(),
    timetableStore.updateSubstitutions(),
    timetableStore.updateEmptyClassrooms(),
    listsStore.updateLists(),
  ])

  if (showSuccess) {
    displaySnackbar('Podatki posodobljeni')
  }
}

export async function updateWrapper(updateFunction: () => Promise<void>) {
  const { displaySnackbar } = useSnackbarStore()

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  try {
    await updateFunction()
  } catch (error) {
    displaySnackbar('Napaka pri pridobivanju podatkov')
    console.error(error)

    // Submit the error to Sentry if enabled
    if (import.meta.env.VITE_SENTRY_ENABLED) captureException(error)

    return
  }

  // Set the data version in storage
  const { dataVersion } = storeToRefs(useSettingsStore())
  dataVersion.value = new Date().toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
}
