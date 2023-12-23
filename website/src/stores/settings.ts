import { defineStore } from 'pinia'

export enum EntityType {
  Class,
  Teacher,
  Classroom,
  EmptyClassrooms,
  None
}

export enum SnackType {
  Normal,
  Vegetarian,
  Poultry,
  Fruitvegetable
}

export enum LunchType {
  Normal,
  Vegetarian
}

export enum MenuType {
  Snack,
  Lunch
}

export enum ThemeType {
  System,
  Light,
  Dark
}

export const useSettingsStore = defineStore('settings', {
  state: () => {
    return {
      entityType: EntityType.Class, // EntityType.None,
      snackType: SnackType.Normal,
      lunchType: LunchType.Normal,

      entities: ['1A'], //[''],

      showSubstitutions: true,
      showLinksInTimetable: true,
      showHoursInTimetable: true,
      showCurrentTime: true,
      enableShowingDetails: true,
      enablePullToRefresh: true,
      enableUpdateOnLoad: true,

      themeType: ThemeType.Light,
      moodleToken: ''
    }
  },

  persist: true
})
