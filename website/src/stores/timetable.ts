import { defineStore } from 'pinia'

import { useSessionStore } from '@/stores/session'
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
      const { currentEntityType, currentEntityList } = useSessionStore()
      const { showSubstitutions } = useSettingsStore()

      if (currentEntityType === EntityType.None) {
        return []
      }

      let timetable: Lesson[] = []
      let substitutions: Substitution[] = []

      if (currentEntityType === EntityType.EmptyClassrooms) {
        // TODO: Substitutions for empty classrooms
        timetable = state.emptyClassrooms
        substitutions = [] // state.substitutions.flat()
      } else {
        for (const entity of currentEntityList) {
          // Get all base lessons that affect the current entity
          timetable.push(
            ...state.timetable.filter(
              (lesson: Lesson) => lesson[currentEntityType as keyof Lesson] === entity,
            ),
          )

          // Get all substitutions that affect the current entity
          substitutions.push(
            ...state.substitutions
              .flat()
              .filter(
                substitution =>
                  substitution[currentEntityType as keyof Substitution] === entity ||
                  substitution[`original-${currentEntityType}` as keyof Substitution] === entity,
              ),
          )
        }
      }

      const lessons: MergedLesson[] = []

      for (const lesson of timetable) {
        // Find a substitution that matches with the current lesson
        const substitution = showSubstitutions
          ? substitutions.find(
              substitution =>
                substitution?.day === lesson.day &&
                substitution?.time === lesson.time &&
                substitution?.['original-teacher'] === lesson.teacher,
            )
          : null

        // Add the lesson with optional substitution to the list
        lessons.push({
          day: lesson.day,
          time: lesson.time,
          subject: lesson.subject,
          class: lesson.class,
          teacher: lesson.teacher,
          classroom: lesson.classroom,
          isSubstitution: !!substitution,
          substitutionSubject: substitution?.subject || null,
          substitutionTeacher: substitution?.teacher || null,
          substitutionClassroom: substitution?.classroom || null,
          notes: substitution?.notes || null,
        })
      }

      // Add substitutions for new lessons
      if (showSubstitutions) {
        for (const substitution of substitutions) {
          if (!substitution['original-teacher']) {
            lessons.push({
              day: substitution.day,
              time: substitution.time,
              subject: null,
              class: substitution.class,
              teacher: substitution['original-teacher'],
              classroom: substitution['original-classroom'],
              isSubstitution: true,
              substitutionSubject: substitution.subject,
              substitutionTeacher: substitution.teacher,
              substitutionClassroom: substitution.classroom,
              notes: substitution.notes,
            })
          }
        }
      }

      // TODO: Fix displaying substitutions for teachers and classrooms

      return lessons
    },

    /**
     * Computes a 3D tensor of lessons organized by time and day.
     *
     * The data are calculated for the currently selected entity and include substitutions
     * if they are enabled.
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
