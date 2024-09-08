import { defineStore } from 'pinia'

import { getCurrentDate, getISODate } from '@/utils/days'
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
    until: string | null
    normal: string | null
    vegetarian: string | null
  } | null
}

export interface LunchSchedule {
  date: string
  time: string | null
  class: string | null
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
        const date = getISODate(getCurrentDate())
        const response = await fetch(import.meta.env.VITE_API + '/menus/week/' + date)
        this.menus = await response.json()
      })
    },

    async updateLunchSchedules() {
      await updateWrapper(async () => {
        const date = getISODate(getCurrentDate())
        const response = await fetch(import.meta.env.VITE_API + '/schedule/week/' + date)
        this.lunchSchedules = await response.json()
      })
    },
  },

  persist: true,
})
