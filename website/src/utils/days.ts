/**
 * Returns the current date.
 */
export function getCurrentDate(): Date {
  if (import.meta.env.VITE_CUSTOM_DATE) {
    // Allow overwriting the current date at build time
    return new Date(import.meta.env.VITE_CUSTOM_DATE)
  }

  return new Date()
}

/**
 * Returns the current day of the week.
 *
 * Days are counted from 0 to 4, where 0 is Monday and 4 is Friday.
 * Days after Friday are counted as Monday (of the next week).
 */
export function getCurrentDay(): number {
  let currentDay = new Date().getDay()
  if (currentDay < 1 || currentDay > 5) currentDay = 1
  return currentDay - 1
}

/**
 * Returns the weekdays of the week of the given date.
 *
 * The weekdays are returned as an array of `Date` objects, where the first
 * element is Monday and the last is Friday. The time of each date is set to
 * the UTC midnight. If the given date is a weekend, the weekdays of the next
 * week are returned.
 */
export function getWeekdays(date: Date): Date[] {
  // Make sure the date is UTC midnight, otherwise, conversion to ISO may be wrong
  date = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))

  if (date.getDay() === 0 || date.getDay() === 6) {
    date.setDate(date.getDate() + 2)
  }

  const monday = new Date(date)
  monday.setDate(date.getDate() - ((date.getDay() + 6) % 7))

  const weekdays: Date[] = []

  for (let i = 0; i < 5; i++) {
    weekdays.push(new Date(monday.getTime() + i * (24 * 60 * 60 * 1000)))
  }

  return weekdays
}

/**
 * Returns the ISO date string of the given date.
 */
export function getISODate(date: Date): string {
  return date.toISOString().split('T')[0]
}
