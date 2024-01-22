import { useMenuStore } from '@/stores/menu'
import { useTimetableStore } from '@/stores/timetable'
import { useDocumentsStore } from '@/stores/documents'
import { useUserStore } from '@/stores/user'
import { useSettingsStore } from '@/stores/settings'

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
  const settingsStore = useSettingsStore()
  const timetableStore = useTimetableStore()
  const userStore = useUserStore()

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
}
