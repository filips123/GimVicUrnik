import { storeToRefs } from 'pinia'

import { useSnackbarStore } from '@/composables/snackbar'
import { useDocumentsStore } from '@/stores/documents'
import { useMenuStore } from '@/stores/menu'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { useTimetableStore } from '@/stores/timetable'
import { useUserStore } from '@/stores/user'

class HTTPError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)

    this.name = 'HTTPError'
    this.status = status
  }
}

export async function fetchHandle(input: RequestInfo, init?: RequestInit): Promise<Response> {
  const response = await fetch(input, init)

  if (!response.ok) {
    throw new HTTPError(`Invalid response status from the API: ${response.status}`, response.status)
  }

  return response
}

export async function updateAllData(): Promise<void> {
  const documentsStore = useDocumentsStore()
  const menuStore = useMenuStore()
  const timetableStore = useTimetableStore()
  const userStore = useUserStore()

  const settingsStore = useSettingsStore()
  const { entityType } = storeToRefs(useSettingsStore())

  const snackbarStore = useSnackbarStore()
  const { displaySnackbar } = snackbarStore

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  await Promise.all([
    documentsStore.updateDocuments(),
    menuStore.updateMenus(),
    menuStore.updateLunchSchedules(),
    settingsStore.updateLists(),
    timetableStore.updateTimetable(),
    timetableStore.updateSubstitutions(),
    timetableStore.updateEmptyClassrooms(),
    userStore.resetEntityToSettings(),
  ])

  if (entityType.value !== EntityType.None) {
    displaySnackbar('Podatki posodobljeni')
  }
}

export function updateWrapper(updateFunction: () => any) {
  const snackbarStore = useSnackbarStore()
  const { displaySnackbar } = snackbarStore

  const { dataVersion } = storeToRefs(useSettingsStore())

  if (!navigator.onLine) {
    displaySnackbar('Internetna povezava ni na voljo')
    return
  }

  try {
    updateFunction()
    dataVersion.value = new Date().toLocaleDateString('sl', { hour: 'numeric', minute: 'numeric' })
  } catch (error) {
    displaySnackbar('Napaka pri pridobivanju podatkov')
    console.error(error)

    // if (import.meta.env.VITE_SENTRY_ENABLED === 'true') captureException(error)
  }
}
