import { defineStore } from 'pinia'
import { getWeekdays } from '@/composables/days'
import { fetchHandle } from '@/composables/update'

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
      lunchSchedules: [] as LunchSchedule[][]
    }
  },

  actions: {
    async updateMenus() {
      /*
      if (!navigator.onLine) {
        displaySnackbar('Internetna povezava ni na voljo')
        return
      }
      */

      /*
      // Reasonable?
      const { enableUpdateOnLoad } = useSettingsStore()
      if (enableUpdateOnLoad || !localStorage.storage || !localStorage.settings) {
        return
      }*/

      // Dates are fixed during development phase
      try {
        this.menus = await Promise.all(
          getWeekdays(new Date('2023-11-27')).map(async (date): Promise<Menu> => {
            const response = await fetchHandle(
              import.meta.env.VITE_API + '/menus/date/' + date.toISOString().split('T')[0]
            )
            const menu = await response.json()
            menu['date'] = date.toISOString().split('T')[0]

            return menu
          })
        )
      } catch (error) {
        // displaySnackbar('Napaka pri pridobivanju podatkov')
        console.error(error)

        // if (import.meta.env.VITE_SENTRY_ENABLED === 'true') captureException(error)
      }
    },

    async updateLunchSchedules() {
      try {
        this.lunchSchedules = await Promise.all(
          getWeekdays(new Date('2023-11-27')).map(async (date): Promise<LunchSchedule[]> => {
            const response = await fetchHandle(
              import.meta.env.VITE_API + '/schedule/date/' + date.toISOString().split('T')[0]
            )
            const lunchSchedule = await response.json()

            return lunchSchedule
          })
        )
      } catch (error) {
        console.error(error)
      }
    }
  }
})
