import { sortEntities } from '@/utils/entities'
import { fetchHandle, updateWrapper } from '@/utils/update'
import { defineStore } from 'pinia'

export enum EntityType {
  Class,
  Teacher,
  Classroom,
  EmptyClassrooms,
  None,
}

export enum SnackType {
  Normal = 'normal',
  Vegetarian = 'vegetarian',
  Poultry = 'poultry',
  Fruitvegetable = 'fruitvegetable',
}

export enum LunchType {
  Normal = 'normal',
  Vegetarian = 'vegetarian',
}

export enum MenuType {
  Snack,
  Lunch,
}

export enum ThemeType {
  System = 'systemTheme',
  Light = 'lightTheme',
  Dark = 'darkTheme',
}

export const useSettingsStore = defineStore('settings', {
  state: () => {
    return {
      entityType: EntityType.None,
      classesList: [] as string[],
      teachersList: [] as string[],
      classroomsList: [] as string[],

      snackType: SnackType.Normal,
      lunchType: LunchType.Normal,

      entities: [''],

      showSubstitutions: true,
      showLinksInTimetable: true,
      showHoursInTimetable: true,
      showCurrentTime: true,
      enableShowingDetails: true,
      enablePullToRefresh: true,
      enableUpdateOnLoad: true,

      dataCollection: true,
      themeType: ThemeType.System,
      moodleToken: '',
      dataVersion: '',

      circularsPassword: '',
    }
  },

  actions: {
    async updateLists() {
      updateWrapper(async () => {
        const responses = await Promise.all([
          fetchHandle(import.meta.env.VITE_API + '/list/classes'),
          fetchHandle(import.meta.env.VITE_API + '/list/teachers'),
          fetchHandle(import.meta.env.VITE_API + '/list/classrooms'),
        ])

        const [classesList, teachersList, classroomsList] = await Promise.all(
          responses.map((response) => response.json()),
        )
        this.classesList = sortEntities(EntityType.Class, classesList)
        this.teachersList = sortEntities(EntityType.Teacher, teachersList)
        this.classroomsList = sortEntities(EntityType.Classroom, classroomsList)
      })
    },
  },

  persist: true,
})
