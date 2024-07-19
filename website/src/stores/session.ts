import { defineStore } from 'pinia'

import { EntityType, useSettingsStore } from '@/stores/settings'
import { getCurrentDay } from '@/utils/days'

export const useSessionStore = defineStore('session', {
  state: () => ({
    day: getCurrentDay(),

    entityType: EntityType.None,
    entityList: [] as string[],
  }),

  actions: {
    resetEntityToSettings() {
      const settingsStore = useSettingsStore()

      this.entityType = settingsStore.entityType
      this.entityList = settingsStore.entityList
    },
  },
})
