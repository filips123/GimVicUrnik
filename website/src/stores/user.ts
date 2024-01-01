import { defineStore } from 'pinia'
import { getCurrentDay } from '@/composables/days'
import { useSettingsStore, EntityType } from '@/stores/settings'

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      day: getCurrentDay(),

      entityType: EntityType.None,
      entities: [''],
    }
  },

  actions: {
    resetData() {
      const settingsStore = useSettingsStore()

      this.entityType = settingsStore.entityType
      this.entities = settingsStore.entities
    },
  },
})
