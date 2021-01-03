import { getModule, Module, MutationAction, VuexModule } from 'vuex-module-decorators'

import store from '@/store'
import { SettingsModule } from '@/store/modules/settings'
import { getMonday, getWeekDays } from '@/utils/days'

export interface Lesson {
  day: number;
  time: number;
  subject: string;
  class: string;
  teacher: string;
  classroom: string;
}

export interface Substitution extends Lesson {
  date: string;
  'original-teacher': string;
  'original-classroom': string;
}

export interface DisplayedLesson {
  day: number;
  time: number;
  subjects: string[];
  classes: string[];
  teachers: string[];
  classrooms: string[];
  substitution: boolean;
}

export function getLessonId (substitution: Lesson): string {
  return `${substitution.day}-${substitution.time}-${substitution.class}-${substitution.teacher}`
}

export function getSubstitutionId (substitution: Substitution): string {
  return `${substitution.day}-${substitution.time}-${substitution.class}-${substitution['original-teacher']}`
}

@Module({ name: 'storage', dynamic: true, preserveState: true, preserveStateType: 'mergeReplaceArrays', store })
class Storage extends VuexModule {
  classList: string[] | null = null
  teacherList: string[] | null = null
  classroomList: string[] | null = null

  timetable: Lesson[] | null = null
  _substitutions: Substitution[][] | null = null

  emptyClassrooms: Lesson[] | null = null

  get substitutions (): Map<string, Substitution> {
    const substitutionMap = new Map()

    // Add keys to substitutions so they can be found more quickly
    for (const substitution of (this._substitutions?.flat() || [])) {
      if (!substitution) continue
      substitutionMap.set(getSubstitutionId(substitution), substitution)
    }

    return substitutionMap
  }

  @MutationAction
  async updateLists () {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.classList
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      // TODO: Display snackbar that user is offline
      return
    }
    if (!shouldUpdateStorage) {
      return
    }

    const responses = await Promise.all([
      fetch(process.env.VUE_APP_API + '/list/classes'),
      fetch(process.env.VUE_APP_API + '/list/teachers'),
      fetch(process.env.VUE_APP_API + '/list/classrooms')
    ])

    const [classList, teacherList, classroomList] = await Promise.all(responses.map(response => response.json()))
    return { classList, teacherList, classroomList }
  }

  @MutationAction
  async updateTimetable () {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.timetable
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      // TODO: Display snackbar that user is offline
      return
    }

    if (!shouldUpdateStorage) {
      return
    }

    const response = await fetch(process.env.VUE_APP_API + '/timetable')
    return { timetable: await response.json() }
  }

  @MutationAction
  async updateSubstitutions () {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state._substitutions
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      // TODO: Display snackbar that user is offline
      return
    }

    if (!shouldUpdateStorage) {
      return
    }

    const responses = await Promise.all(getWeekDays(getMonday(new Date())).map(date => fetch(process.env.VUE_APP_API + '/substitutions/date/' + date.toISOString().split('T')[0])))
    const _substitutions = await Promise.all(responses.map(response => response.json()))

    return { _substitutions }
  }

  @MutationAction
  async updateEmptyClassrooms () {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.emptyClassrooms
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      // TODO: Display snackbar that user is offline
      return
    }

    if (!shouldUpdateStorage) {
      return
    }

    const response = await fetch(process.env.VUE_APP_API + '/timetable/classrooms/empty')
    return { emptyClassrooms: await response.json() }
  }
}

export const StorageModule = getModule(Storage)
