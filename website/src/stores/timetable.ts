import { EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { getWeekdays } from '@/utils/days'
import { fetchHandle, updateWrapper } from '@/utils/update'
import { defineStore } from 'pinia'

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
    }
  },

  getters: {
    lessons(state) {
      const userStore = useUserStore()
      const { entities, entityType } = userStore

      let timetable: Lesson[] = []
      let substitutions: Substitution[] = []

      if (entityType == EntityType.None) {
        return []
      } else if (entityType == EntityType.EmptyClassrooms) {
        timetable = state.emptyClassrooms
      } else {
        for (const entity of entities) {
          timetable = timetable.concat(
            state.timetable.filter(
              (lesson: Lesson) => lesson[entityType as keyof Lesson] == entity,
            ),
          )
          for (const substitutionsDay of state.substitutions) {
            substitutions = substitutions.concat(
              substitutionsDay.filter(
                (substitution) => substitution[entityType as keyof Substitution] == entity,
              ),
            )
          }
        }
      }

      const lessons: MergedLesson[] = []

      for (const lesson of timetable) {
        const substitution = substitutions.find(
          (substitution) =>
            substitution?.day === lesson.day &&
            substitution?.time === lesson.time &&
            substitution?.['original-teacher'] === lesson.teacher,
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
          notes: substitution?.notes || '',
        })
      }

      return lessons
    },
  },

  actions: {
    async updateTimetable() {
      updateWrapper(async () => {
        const response = await fetchHandle(import.meta.env.VITE_API + '/timetable')
        this.timetable = await response.json()
      })
    },

    async updateSubstitutions() {
      updateWrapper(async () => {
        const responses = await Promise.all(
          getWeekdays(new Date()).map((date) =>
            fetchHandle(
              import.meta.env.VITE_API + '/substitutions/date/' + date.toISOString().split('T')[0],
            ),
          ),
        )
        this.substitutions = await Promise.all(responses.map((response) => response.json()))
      })
    },

    async updateEmptyClassrooms() {
      updateWrapper(async () => {
        const response = await fetchHandle(import.meta.env.VITE_API + '/timetable/classrooms/empty')
        this.emptyClassrooms = await response.json()
      })
    },
  },

  persist: true,
})
