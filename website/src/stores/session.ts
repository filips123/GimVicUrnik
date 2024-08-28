import { defineStore } from 'pinia'

import { EntityType, useSettingsStore } from '@/stores/settings'
import { getCurrentDay } from '@/utils/days'

export const useSessionStore = defineStore('session', {
  state: () => ({
    day: getCurrentDay(),

    currentEntityType: EntityType.None,
    currentEntityList: [] as string[],
  }),

  actions: {
    resetEntityToSettings() {
      const settingsStore = useSettingsStore()

      this.currentEntityType = settingsStore.entityType
      this.currentEntityList = settingsStore.entityList
    },
  },
})
