import { defineStore } from 'pinia'

import { EntityType } from '@/stores/settings'
import { sortEntities } from '@/utils/entities'
import { updateWrapper } from '@/utils/update'

export const useListsStore = defineStore('lists', {
  state: () => ({
    classesList: [] as string[],
    teachersList: [] as string[],
    classroomsList: [] as string[],
  }),

  actions: {
    async updateLists() {
      await updateWrapper(async () => {
        const responses = await Promise.all([
          fetch(import.meta.env.VITE_API + '/list/classes'),
          fetch(import.meta.env.VITE_API + '/list/teachers'),
          fetch(import.meta.env.VITE_API + '/list/classrooms'),
        ])

        const [classesList, teachersList, classroomsList] = await Promise.all(
          responses.map(response => response.json()),
        )

        this.classesList = sortEntities(EntityType.Class, classesList)
        this.teachersList = sortEntities(EntityType.Teacher, teachersList)
        this.classroomsList = sortEntities(EntityType.Classroom, classroomsList)
      })
    },
  },

  persist: true,
})
