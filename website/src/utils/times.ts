export const lessonTimes: [string, string][] = [
  ['7:10', '7:55'],
  ['8:00', '8:45'],
  ['8:50', '9:35'],
  ['9:40', '10:25'],
  ['10:55', '11:40'],
  ['11:45', '12:30'],
  ['12:35', '13:20'],
  ['13:25', '14:10'],
  ['14:15', '15:00'],
  ['15:05', '15:50'],
  ['15:55', '16:40'],
]

export function getCurrentTime(): number {
  const time = new Date()
  const startDateTime = new Date()
  const endDateTime = new Date()

  let timeIndex = 0

  for (let i = 0; i < lessonTimes.length; i++) {
    // Current time starts at the end of the previous lesson (except for pre-lessons)
    // and ends on the end of the current lesson
    const startTimes = lessonTimes[i > 0 ? i - 1 : i][i > 0 ? 1 : 0].split(':').map(Number)
    const endTimes = lessonTimes[i][1].split(':').map(Number)

    startDateTime.setHours(startTimes[0], startTimes[1], 0)
    endDateTime.setHours(endTimes[0], endTimes[1], 0)

    if (startDateTime <= time && time <= endDateTime) return timeIndex
    timeIndex++
  }

  return -1
}
