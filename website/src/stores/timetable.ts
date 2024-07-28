import { defineStore } from 'pinia'

import { useSessionStore } from '@/stores/session'
import { EntityType } from '@/stores/settings'
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
  isSubstitution: boolean
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
    lessonsList(state): MergedLesson[] {
      const sessionStore = useSessionStore()
      const { currentEntityType, currentEntityList } = sessionStore

      if (currentEntityType === EntityType.None) {
        return []
      }

      let timetable: Lesson[] = []
      let substitutions: Substitution[] = []

      if (currentEntityType === EntityType.EmptyClassrooms) {
        // TODO: Substitutions for empty classrooms
        timetable = state.emptyClassrooms
      } else {
        for (const entity of currentEntityList) {
          timetable = timetable.concat(
            state.timetable.filter(
              (lesson: Lesson) => lesson[currentEntityType as keyof Lesson] === entity,
            ),
          )
          for (const substitutionsDay of state.substitutions) {
            substitutions = substitutions.concat(
              substitutionsDay.filter(
                substitution => substitution[currentEntityType as keyof Substitution] === entity,
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
          isSubstitution: !!substitution,
          substitutionClassroom: substitution?.classroom || '',
          substitutionSubject: substitution?.subject || '',
          substitutionTeacher: substitution?.teacher || '',
          notes: substitution?.notes || '',
        })
      }

      // TODO: Substitutions when there are no initial lessons

      return lessons
    },

    /**
     * Computes a 3D tensor of lessons organized by time and day.
     *
     * The data are calculated for the currently selected entity and include substitutions.
     *
     * @returns A 3D tensor where the first dimension represents time slots, the second dimension
     * represents days, and the third dimension contains lessons for that time and day.
     */
    lessonsTensor(): MergedLesson[][][] {
      const days = 5
      const times = 11

      const tensor: MergedLesson[][][] = Array.from(Array(times), () => new Array(days).fill([]))

      for (const lesson of this.lessonsList) {
        tensor[lesson.time][lesson.day - 1] = tensor[lesson.time][lesson.day - 1].concat(lesson)
      }

      return tensor
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
