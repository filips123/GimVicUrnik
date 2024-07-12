import { defineStore } from 'pinia'

export enum EntityType {
  Class = 'class',
  Teacher = 'teacher',
  Classroom = 'classroom',
  EmptyClassrooms = 'emptyClassrooms',
  None = 'none',
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
  state: () => ({
    entityType: EntityType.None,
    entityList: [] as string[],

    snackType: SnackType.Normal,
    lunchType: LunchType.Normal,

    showSubstitutions: true,
    showLinksInTimetable: true,
    showHoursInTimetable: true,
    showCurrentTime: true,
    enableLessonDetails: true,
    enablePullToRefresh: true,

    dataCollectionPerformance: navigator.doNotTrack !== '1' && !navigator.globalPrivacyControl,
    dataCollectionCrashes: true,

    themeType: ThemeType.System,

    moodleToken: '',
    circularsPassword: '',
  }),

  persist: true,
})
