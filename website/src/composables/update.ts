import { useMenuStore } from '@/stores/menu'
import { useTimetableStore } from '@/stores/timetable'
import { useDocumentsStore } from '@/stores/documents'

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
  const menuStore = useMenuStore()
  const timetableStore = useTimetableStore()
  const documentsStore = useDocumentsStore()

  await Promise.all([
    menuStore.updateLunchSchedules(),
    menuStore.updateMenus(),
    timetableStore.updateLists(),
    documentsStore.updateDocuments()
  ])

  // displaySnackbar('Podatki posodobljeni')
}
