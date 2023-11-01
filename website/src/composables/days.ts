export function getCurrentDay(): number {
  let currentDay = new Date().getDay()

  if (currentDay < 1 || currentDay > 5) {
    currentDay = 1
  }

  return currentDay - 1
}

export function getWeekDays(date: Date): Date[] {
  if (date.getDay() === 0 || date.getDay() === 6) {
    date.setDate(date.getDate() + 2)
  }

  const monday = new Date(date)
  monday.setDate(date.getDate() - ((date.getDay() + 6) % 7))

  const weekDays: Date[] = []

  for (let i = 0; i < 5; i++) {
    weekDays.push(new Date(monday.getTime() + i * (24 * 60 * 60 * 1000)))
  }

  return weekDays
}
