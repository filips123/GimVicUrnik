export function getCurrentDay (): number {
  let currentDay = (new Date()).getDay()
  if (currentDay > 5) currentDay = 1
  if (currentDay < 1) currentDay = 1

  return currentDay - 1
}

export function getMonday (date: Date): Date {
  const day = date.getDay()
  let diff = date.getDate() - day + 1

  if (day === 6) diff = date.getDate() + 2
  if (day === 0) diff = date.getDate() + 1

  return new Date(date.setDate(diff))
}

export function getWeekDays (monday: Date): Date[] {
  const days: Date[] = []

  for (let i = 0; i < 5; i++) {
    days.push(new Date(monday.getTime() + i * (24 * 60 * 60 * 1000)))
  }

  return days
}

export const daysInWeek = ['Ponedeljek', 'Torek', 'Sreda', 'Četrtek', 'Petek']
