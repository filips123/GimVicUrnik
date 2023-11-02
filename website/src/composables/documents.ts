import { useSettingsStore } from '@/stores/settings'

// Add moodle token if set
export function tokenizeUrl(url: string): string {
  const settingsStore = useSettingsStore()

  const pluginFileWebserviceUrl = import.meta.env.VITE_ECLASSROOM_WEBSERVICE
  const pluginFileNormalUrl = import.meta.env.VITE_ECLASSROOM_NORMAL
  const moodleToken = settingsStore.moodleToken

  if (moodleToken && url.includes(pluginFileNormalUrl)) {
    return url.replace(pluginFileNormalUrl, pluginFileWebserviceUrl) + `?token=${moodleToken}`
  }

  return url
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('sl')
}
