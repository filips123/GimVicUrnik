import { defineStore } from 'pinia'

import { getWeekdays } from '@/utils/days'
import { fetchHandle, updateWrapper } from '@/utils/update'

export interface Menu {
  date: string
  snack: {
    normal: string | null
    vegetarian: string | null
    poultry: string | null
    fruitvegetable: string | null
  }
  lunch: {
    normal: string | null
    vegetarian: string | null
  }
}

export interface LunchSchedule {
  date: string
  time: string | null
  notes: string | null
  class: string
  location: string | null
}

export const useMenuStore = defineStore('menu', {
  state: () => {
    return {
      menus: [] as Menu[],
      lunchSchedules: [] as LunchSchedule[][],
    }
  },

  actions: {
    async updateMenus() {
      updateWrapper(async () => {
        this.menus = await Promise.all(
          getWeekdays(new Date()).map(async (date): Promise<Menu> => {
            const response = await fetchHandle(
              import.meta.env.VITE_API + '/menus/date/' + date.toISOString().split('T')[0],
            )
            const menu = await response.json()
            menu['date'] = date.toISOString().split('T')[0]

            return menu
          }),
        )
      })
    },

    async updateLunchSchedules() {
      updateWrapper(async () => {
        this.lunchSchedules = await Promise.all(
          getWeekdays(new Date()).map(async (date): Promise<LunchSchedule[]> => {
            const response = await fetchHandle(
              import.meta.env.VITE_API + '/schedule/date/' + date.toISOString().split('T')[0],
            )
            const lunchSchedule = await response.json()

            return lunchSchedule
          }),
        )
      })
    },
  },

  persist: true,
})
