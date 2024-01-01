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
]

export function getCurrentTime(): number {
  const time = new Date()
  const startDateTime = new Date()
  const endDateTime = new Date()

  let timeIndex = 0
  for (const [startTime, endTime] of lessonTimes) {
    const startTimes = startTime.split(':').map(Number)
    const endTimes = endTime.split(':').map(Number)

    startDateTime.setHours(startTimes[0], startTimes[1], 0)
    endDateTime.setHours(endTimes[0], endTimes[1] + 5, 0)

    if (startDateTime <= time && time <= endDateTime) {
      return timeIndex
    }
    timeIndex++
  }

  return -1
}
