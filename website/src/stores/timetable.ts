import { defineStore } from 'pinia'

import { EntityType, useSettingsStore } from '@/stores/settings'
import { getCurrentDate, getISODate, getWeekdays } from '@/utils/days'
import { fetchHandle, updateWrapper } from '@/utils/update'

export interface Lesson {
  day: number
  time: number
  subject: string | null
  class: string | null
  teacher: string | null
  classroom: string | null
}

export interface Substitution extends Lesson {
  date: string
  notes: string | null
  'original-teacher': string | null
  'original-classroom': string | null
}

export interface MergedLesson {
  day: number
  time: number
  subject: string | null
  class: string | null
  teacher: string | null
  classroom: string | null
  substitution: boolean
  substitutionSubject: string | null
  substitutionTeacher: string | null
  substitutionClassroom: string | null
  notes: string | null
}

export const useTimetableStore = defineStore('timetable', {
  state: () => ({
    timetable: [] as Lesson[],
    substitutions: [] as Substitution[][],

    emptyClassrooms: [] as Lesson[],
  }),

  getters: {
    lessons(state): MergedLesson[] {
      const sessionStore = useSettingsStore()
      const { entityList: entities, entityType: type } = sessionStore

      if (type === EntityType.None) {
        return []
      }

      let timetable: Lesson[] = []
      let substitutions: Substitution[] = []

      if (type == EntityType.None) {
        return []
      } else if (type == EntityType.EmptyClassrooms) {
        timetable = state.emptyClassrooms
      } else {
        for (const entity of entities) {
          timetable = timetable.concat(
            state.timetable.filter((lesson: Lesson) => lesson[type as keyof Lesson] == entity),
          )
          for (const substitutionsDay of state.substitutions) {
            substitutions = substitutions.concat(
              substitutionsDay.filter(
                substitution => substitution[type as keyof Substitution] == entity,
              ),
            )
          }
        }
      }

      const lessons: MergedLesson[] = []

      for (const lesson of timetable) {
        const substitution = substitutions.find(
          substitution =>
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
        const dates = getWeekdays(getCurrentDate()).map(date => getISODate(date))
        const urls = dates.map(date => import.meta.env.VITE_API + '/substitutions/date/' + date)
        const responses = await Promise.all(urls.map(url => fetchHandle(url)))
        this.substitutions = await Promise.all(responses.map(response => response.json()))
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
