import { useSettingsStore } from '@/stores/settings'

// Add moodle token if set
export function tokenizeUrl(url: string): string {
  const settingsStore = useSettingsStore()
  const { moodleToken } = settingsStore

  const pluginFileWebserviceUrl = import.meta.env.VITE_ECLASSROOM_WEBSERVICE
  const pluginFileNormalUrl = import.meta.env.VITE_ECLASSROOM_NORMAL

  if (moodleToken && url.includes(pluginFileNormalUrl)) {
    return url.replace(pluginFileNormalUrl, pluginFileWebserviceUrl) + `?token=${moodleToken}`
  }

  return url
}
