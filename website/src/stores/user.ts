import { defineStore } from 'pinia'
import { getCurrentDay } from '@/composables/days'
import { useSettingsStore, EntityType } from '@/stores/settings'

export const useUserStore = defineStore('user', {
  state: () => {
    return {
      day: getCurrentDay(),

      entityType: EntityType.EmptyClassrooms,
      classes: [] as string[],
      teachers: [] as string[],
      classrooms: [] as string[]
    }
  },

  getters: {
    getCurrentEntities(state) {
      switch (state.entityType) {
        case EntityType.Class:
          return state.classes
        case EntityType.Teacher:
          return state.teachers
        case EntityType.Classroom:
          return state.classrooms
      }

      return ['']
    }
  },

  actions: {
    resetData() {
      const settingsStore = useSettingsStore()

      this.entityType = settingsStore.entityType
      this.classes = settingsStore.classes
      this.teachers = settingsStore.teachers
      this.classrooms = settingsStore.classrooms
    },

    changeEntity(entityType: EntityType, entity: string) {
      this.entityType = entityType

      switch (entityType) {
        case EntityType.Class:
          this.classes = [entity]
        case EntityType.Teacher:
          this.teachers = [entity]
        case EntityType.Classroom:
          this.classrooms = [entity]
      }
    }
  }
})
