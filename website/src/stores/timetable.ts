import { defineStore } from 'pinia'
import { fetchHandle } from '@/composables/update'
import { getWeekdays } from '@/composables/days'
import { EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

export interface Lesson {
  day: number
  time: number
  subject: string
  class: string
  teacher: string
  classroom: string
}

export interface Substitution extends Lesson {
  date: string
  notes: string
  'original-teacher': string
  'original-classroom': string
}

export interface MergedLesson {
  day: number
  time: number
  class: string
  classroom: string
  subject: string
  teacher: string
  substitution: boolean
  substitutionClassroom: string
  substitutionSubject: string
  substitutionTeacher: string
  notes: string
}

export const useTimetableStore = defineStore('timetable', {
  state: () => {
    return {
      timetable: [] as Lesson[],
      emptyClassrooms: [] as Lesson[],
      substitutions: [] as Substitution[][],

      classesList: [] as String[],
      teachersList: [] as String[],
      classroomsList: [] as String[]
    }
  },

  getters: {
    lessons(state) {
      const userStore = useUserStore()

      let timetable: Lesson[] = []
      let substitutions: Substitution[] = []

      switch (userStore.entityType) {
        case EntityType.Class:
          for (const class_ of userStore.entities) {
            timetable = timetable.concat(state.timetable.filter((lesson) => lesson.class == class_))
            for (const substitutionsDay of state.substitutions) {
              substitutions = substitutions.concat(
                substitutionsDay.filter((substitution) => substitution.class == class_)
              )
            }
          }
          break
        case EntityType.Teacher:
          for (const teacher of userStore.entities) {
            timetable = timetable.concat(
              state.timetable.filter((lesson) => lesson.teacher == teacher)
            )
            for (const substitutionsDay of state.substitutions) {
              substitutions = substitutions.concat(
                substitutionsDay.filter((substitution) => substitution.teacher == teacher)
              )
            }
          }
          break
        case EntityType.Classroom:
          for (const classroom of userStore.entities) {
            timetable = timetable.concat(
              state.timetable.filter((lesson) => lesson.classroom == classroom)
            )
            for (const substitutionsDay of state.substitutions) {
              substitutions = substitutions.concat(
                substitutionsDay.filter((substitution) => substitution.classroom == classroom)
              )
            }
          }
          break
        case EntityType.EmptyClassrooms:
          timetable = state.emptyClassrooms
      }

      const lessons: MergedLesson[] = []

      for (const lesson of timetable) {
        let substitution = substitutions.find(
          (substitution) =>
            substitution?.day === lesson.day &&
            substitution?.time === lesson.time &&
            substitution?.['original-teacher'] === lesson.teacher
        )

        lessons.push({
          day: lesson.day,
          time: lesson.time,
          class: lesson.class,
          classroom: lesson.classroom,
          subject: lesson.subject,
          teacher: lesson.teacher,
          substitution: !!substitution,
          substitutionClassroom: substitution?.classroom || '',
          substitutionSubject: substitution?.subject || '',
          substitutionTeacher: substitution?.teacher || '',
          notes: substitution?.notes || ''
        })
      }

      return lessons
    }
  },

  actions: {
    async updateTimetable() {
      try {
        const response = await fetchHandle(import.meta.env.VITE_API + '/timetable')
        this.timetable = await response.json()
      } catch (error) {
        console.error(error)
      }
    },

    async updateSubstitutions() {
      try {
        const responses = await Promise.all(
          getWeekdays(new Date('2023-11-27')).map((date) =>
            fetchHandle(
              import.meta.env.VITE_API + '/substitutions/date/' + date.toISOString().split('T')[0]
            )
          )
        )
        this.substitutions = await Promise.all(responses.map((response) => response.json()))
      } catch (error) {
        console.error(error)
      }
    },

    async updateEmptyClassrooms() {
      try {
        const response = await fetchHandle(import.meta.env.VITE_API + '/timetable/classrooms/empty')
        this.emptyClassrooms = await response.json()
      } catch (error) {
        console.error(error)
      }
    },

    async updateLists() {
      try {
        const responses = await Promise.all([
          fetchHandle(import.meta.env.VITE_API + '/list/classes'),
          fetchHandle(import.meta.env.VITE_API + '/list/teachers'),
          fetchHandle(import.meta.env.VITE_API + '/list/classrooms')
        ])

        const [classesList, teachersList, classroomsList] = await Promise.all(
          responses.map((response) => response.json())
        )
        this.classesList = classesList
        this.teachersList = teachersList
        this.classroomsList = classroomsList
      } catch (error) {
        console.error(error)
      }
    }
  },

  persist: true
})
