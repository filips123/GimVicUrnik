export function tokenizeUrl(url: string, moodleToken: string): string {
  const pluginFileWebserviceUrl = import.meta.env.VITE_ECLASSROOM_WEBSERVICE
  const pluginFileNormalUrl = import.meta.env.VITE_ECLASSROOM_NORMAL

  if (moodleToken && url.includes(pluginFileNormalUrl)) {
    return url.replace(pluginFileNormalUrl, pluginFileWebserviceUrl) + `?token=${moodleToken}`
  }

  return url
}
