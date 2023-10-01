import { defineStore } from 'pinia'
import { getCurrentDay } from '@/composables/days'

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      day: getCurrentDay()
    }
  }
})
