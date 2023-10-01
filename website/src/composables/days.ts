export function getCurrentDay(): number {
  let currentDay = new Date().getDay()

  if (currentDay < 1 || currentDay > 5) {
    currentDay = 1
  }

  return currentDay - 1
}
