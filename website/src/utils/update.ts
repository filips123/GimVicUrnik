import { useSnackbarStore } from '@/composables/snackbar'
import { useDocumentsStore } from '@/stores/documents'
import { useFoodStore } from '@/stores/food'
import { useListsStore } from '@/stores/lists'
import { useTimetableStore } from '@/stores/timetable'

class HTTPError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)

    this.name = 'HTTPError'
    this.status = status
  }
}

export async function fetchHandle(input: RequestInfo, init?: RequestInit): Promise<Response> {
  // TODO: Maybe replace with proper Sentry integration

  const response = await fetch(input, init)

  if (!response.ok) {
    throw new HTTPError(`Invalid response status from the API: ${response.status}`, response.status)
  }

  return response
}

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

export function updateWrapper(updateFunction: () => any) {
  const snackbarStore = useSnackbarStore()
  const { displaySnackbar } = snackbarStore

  // TODO: Update data version displayed in settings
  // TODO: Configure Sentry error capturing

  // const { dataVersion } = storeToRefs(useSettingsStore())

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  try {
    updateFunction()
    // dataVersion.value = new Date().toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
  } catch (error) {
    alert(1)
    displaySnackbar('Napaka pri pridobivanju podatkov')
    console.error(error)

    // if (import.meta.env.VITE_SENTRY_ENABLED === 'true') captureException(error)
  }
}
