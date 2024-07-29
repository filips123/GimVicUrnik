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
    /**
     * Computes a 3D array of lessons organized by time and day.
     *
     * The lessons are filtered based on whether they affect the currently selected entity.
     *
     * If enabled, substitutions are also included in the array, merged with the base lessons
     * if possible.
     *
     * @returns A 3D array where the first dimension represents time slots, the second dimension
     * represents days, and the third dimension contains lessons for that time and day.
     */
    lessons(state): MergedLesson[][][] {
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
        substitutions = []
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

      // Calculate the maximum time of any lessons
      const maxTime = Math.max(
        ...timetable.map(lesson => lesson.time),
        ...substitutions.map(substitution => substitution.time),
      )

      // Create a 3D array of lessons organized by time and day
      const array: MergedLesson[][][] = Array.from({ length: maxTime + 1 }, () =>
        Array.from({ length: 5 }, () => []),
      )

      for (const lesson of timetable) {
        // Find a substitution that matches with the current lesson (teacher)
        // Note that there may be multiple matching substitutions, but we only take the first one
        // This should be fine since they should be equivalent, apart from minor details
        const substitution = showSubstitutions
          ? substitutions.find(
              substitution =>
                substitution?.day === lesson.day &&
                substitution?.time === lesson.time &&
                substitution?.['original-teacher'] === lesson.teacher,
            )
          : null

        // Add the lesson with the optional substitution to the array
        array[lesson.time][lesson.day - 1].push({
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

      if (showSubstitutions) {
        // Add all effective substitutions to the array
        // This probably includes duplicates, but we handle that below
        for (const substitution of substitutions) {
          array[substitution.time][substitution.day - 1].push({
            day: substitution.day,
            time: substitution.time,
            subject: substitution['original-teacher'] ? substitution.subject : null,
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

        // Deduplicate all lessons and substitutions
        for (let timeIndex = 0; timeIndex < array.length; timeIndex++) {
          for (let dayIndex = 0; dayIndex < array[timeIndex].length; dayIndex++) {
            const uniqueLessons = new Map<string, MergedLesson>()

            for (const [index, lesson] of array[timeIndex][dayIndex].entries()) {
              // We want to keep normal lessons as they are
              if (!lesson.isSubstitution) {
                uniqueLessons.set(`NORMAL-${index}`, lesson)
                continue
              }

              // We want to deduplicate substitutions that have the original teacher and displayed data
              const key = `SUBSTITUTION-${lesson.class}-${lesson.teacher}-${lesson.substitutionSubject}-${lesson.substitutionTeacher}-${lesson.substitutionClassroom}`

              // We want to keep the first lesson with notes if any of them has notes, otherwise the first one overall
              if (!uniqueLessons.has(key) || uniqueLessons.get(key)?.notes === null) {
                uniqueLessons.set(key, lesson)
              }
            }

            array[timeIndex][dayIndex] = Array.from(uniqueLessons.values())
          }
        }
      }

      return array
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
