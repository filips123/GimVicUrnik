import { captureException } from '@sentry/browser'
import { storeToRefs } from 'pinia'

import { useSnackbarStore } from '@/composables/snackbar'
import { useDocumentsStore } from '@/stores/documents'
import { useFoodStore } from '@/stores/food'
import { useListsStore } from '@/stores/lists'
import { useSettingsStore } from '@/stores/settings'
import { useTimetableStore } from '@/stores/timetable'

type SportsSection = 'schedule' | 'football' | 'volleyball' | 'basketball'

export async function updateAllData(
  showSuccess: boolean = true,
  sportsSection?: SportsSection,
): Promise<void> {
  const { displaySnackbar } = useSnackbarStore()

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  if (showSuccess) {
    displaySnackbar('Posodabljanje ...')
  }

  // Sports are intentionally imported only while the sports route is visible.
  // This keeps the store and its API client out of the initial timetable/menu bundle.
  if (sportsSection) {
    const [{ useSportsStore }, { getCurrentDate, getISODate }] = await Promise.all([
      import('@/stores/sports'),
      import('@/utils/days'),
    ])
    const sportsStore = useSportsStore()
    await (sportsSection === 'schedule'
      ? sportsStore.updateSchedule(getISODate(getCurrentDate()))
      : sportsStore.updateSport(sportsSection))

    if (showSuccess) displaySnackbar('Podatki posodobljeni')
    return
  }

  const documentsStore = useDocumentsStore()
  const foodStore = useFoodStore()
  const timetableStore = useTimetableStore()
  const listsStore = useListsStore()

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
  if (!navigator.onLine) {
    return
  }

  try {
    await updateFunction()
  } catch (error) {
    // Inform the user about the error
    const { displaySnackbar } = useSnackbarStore()
    displaySnackbar('Napaka pri pridobivanju podatkov')

    // Log the error to the console
    console.error(error)

    // Submit the error to Sentry if enabled
    if (import.meta.env.VITE_SENTRY_ENABLED) captureException(error)

    return
  }

  // Set the data version in storage
  const { dataVersion } = storeToRefs(useSettingsStore())
  dataVersion.value = new Date().toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
}
