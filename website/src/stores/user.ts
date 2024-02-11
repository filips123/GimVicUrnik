import { EntityType, useSettingsStore } from '@/stores/settings'
import { getCurrentDay } from '@/utils/days'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      day: getCurrentDay(),

      entityType: EntityType.None,
      entities: [''],
    }
  },

  actions: {
    resetEntityToSettings() {
      const settingsStore = useSettingsStore()

      this.entityType = settingsStore.entityType
      this.entities = settingsStore.entities
    },
  },
})
