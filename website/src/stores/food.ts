import { defineStore } from 'pinia'

import { getCurrentDate, getISODate, getWeekdays } from '@/utils/days'
import { updateWrapper } from '@/utils/update'

export interface Menu {
  date: string
  snack: {
    normal: string | null
    vegetarian: string | null
    poultry: string | null
    fruitvegetable: string | null
  } | null
  lunch: {
    normal: string | null
    vegetarian: string | null
  } | null
}

export interface LunchSchedule {
  class: string
  date: string
  time: string | null
  notes: string | null
  location: string | null
}

export const useFoodStore = defineStore('food', {
  state: () => ({
    menus: [] as Menu[],
    lunchSchedules: [] as LunchSchedule[][],
  }),

  actions: {
    async updateMenus() {
      await updateWrapper(async () => {
        this.menus = await Promise.all(
          getWeekdays(getCurrentDate()).map(async (date): Promise<Menu> => {
            const iso = getISODate(date)
            const response = await fetch(import.meta.env.VITE_API + '/menus/date/' + iso)
            return { ...(await response.json()), date: iso }
          }),
        )
      })
    },

    async updateLunchSchedules() {
      await updateWrapper(async () => {
        this.lunchSchedules = await Promise.all(
          getWeekdays(getCurrentDate()).map(async (date): Promise<LunchSchedule[]> => {
            const iso = getISODate(date)
            const response = await fetch(import.meta.env.VITE_API + '/schedule/date/' + iso)
            return await response.json()
          }),
        )
      })
    },
  },

  persist: true,
})
