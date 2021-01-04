import { getModule, Module, MutationAction, VuexModule } from 'vuex-module-decorators'

import store from '@/store'
import { SettingsModule } from '@/store/modules/settings'
import { getMonday, getWeekDays } from '@/utils/days'
import { displaySnackbar } from '@/utils/snackbar'

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

export async function updateAllData (): Promise<void> {
  await Promise.all([
    StorageModule.updateLists(true),
    StorageModule.updateTimetable(true),
    StorageModule.updateEmptyClassrooms(true),
    StorageModule.updateSubstitutions(true)
  ])

  displaySnackbar('Podatki posodobljeni')
}

@Module({ name: 'storage', dynamic: true, preserveState: true, preserveStateType: 'mergeReplaceArrays', store })
class Storage extends VuexModule {
  lastUpdated: Date | null = null

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
  async updateLists (forceUpdate = false) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.classList
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      displaySnackbar('Internetna povezava ni na voljo')
      return
    }
    if (!forceUpdate && !shouldUpdateStorage) {
      return
    }

    const responses = await Promise.all([
      fetch(process.env.VUE_APP_API + '/list/classes'),
      fetch(process.env.VUE_APP_API + '/list/teachers'),
      fetch(process.env.VUE_APP_API + '/list/classrooms')
    ])

    const [classList, teacherList, classroomList] = await Promise.all(responses.map(response => response.json()))
    const lastUpdated = new Date()

    return { classList, teacherList, classroomList, lastUpdated }
  }

  @MutationAction
  async updateTimetable (forceUpdate = false) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.timetable
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      displaySnackbar('Internetna povezava ni na voljo')
      return
    }

    if (!forceUpdate && !shouldUpdateStorage) {
      return
    }

    const response = await fetch(process.env.VUE_APP_API + '/timetable')
    return { timetable: await response.json(), lastUpdated: new Date() }
  }

  @MutationAction
  async updateSubstitutions (forceUpdate = false) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state._substitutions
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      displaySnackbar('Internetna povezava ni na voljo')
      return
    }

    if (!forceUpdate && !shouldUpdateStorage) {
      return
    }

    const responses = await Promise.all(getWeekDays(getMonday(new Date())).map(date => fetch(process.env.VUE_APP_API + '/substitutions/date/' + date.toISOString().split('T')[0])))
    const _substitutions = await Promise.all(responses.map(response => response.json()))
    const lastUpdated = new Date()

    return { _substitutions, lastUpdated }
  }

  @MutationAction
  async updateEmptyClassrooms (forceUpdate = false) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    const isStoredLocally = 'storage' in localStorage && this.state.emptyClassrooms
    const shouldUpdateStorage = !isStoredLocally || !('settings' in localStorage) || SettingsModule.enableUpdateOnLoad

    if (!navigator.onLine) {
      displaySnackbar('Internetna povezava ni na voljo')
      return
    }

    if (!forceUpdate && !shouldUpdateStorage) {
      return
    }

    const response = await fetch(process.env.VUE_APP_API + '/timetable/classrooms/empty')
    return { emptyClassrooms: await response.json(), lastUpdated: new Date() }
  }
}

export const StorageModule = getModule(Storage)
