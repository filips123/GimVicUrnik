import { useMenuStore } from '@/stores/menu'
import { useTimetableStore } from '@/stores/timetable'
import { useDocumentsStore } from '@/stores/documents'
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
  const useStore = useUserStore()
  const menuStore = useMenuStore()
  const timetableStore = useTimetableStore()
  const documentsStore = useDocumentsStore()

  await Promise.all([
    documentsStore.updateDocuments(),
    useStore.resetData(),
    menuStore.updateLunchSchedules(),
    menuStore.updateMenus(),
    timetableStore.updateLists(),
    timetableStore.updateTimetable(),
    timetableStore.updateSubstitutions(),
    timetableStore.updateEmptyClassrooms(),
    timetableStore.updateEmptyClassrooms(),
  ])

  // displaySnackbar('Podatki posodobljeni')
}
