import { defineStore } from 'pinia'
import { fetchHandle } from '@/composables/update'

export const useTimetableStore = defineStore('timetable', {
  state: () => {
    return {
      classList: [] as String[],
      teachersList: [] as String[],
      classroomsList: [] as String[]
    }
  },

  actions: {
    async updateLists() {
      try {
        const responses = await Promise.all([
          fetchHandle(import.meta.env.VITE_API + '/list/classes'),
          fetchHandle(import.meta.env.VITE_API + '/list/teachers'),
          fetchHandle(import.meta.env.VITE_API + '/list/classrooms')
        ])

        const [classList, teachersList, classroomsList] = await Promise.all(
          responses.map((response) => response.json())
        )
        this.classList = classList
        this.teachersList = teachersList
        this.classroomsList = classroomsList
      } catch (error) {
        console.error(error)
      }
    }
  }
})
