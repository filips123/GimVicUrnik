import { defineStore } from 'pinia'

import { AccentColorName } from '@/utils/colors'

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
  Snack = 'snack',
  Lunch = 'lunch',
}

export enum ThemeType {
  System = 'system',
  Light = 'light',
  Dark = 'dark',
}

function validateEnum<T extends object>(
  enumObject: T,
  value: any,
  defaultValue: T[keyof T],
): T[keyof T] {
  return Object.values(enumObject).includes(value) ? value : defaultValue
}

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    entityType: EntityType.None,
    entityList: [] as string[],

    snackType: SnackType.Normal,
    lunchType: LunchType.Normal,

    showSubstitutions: true,
    showLinksInTimetable: true,
    showDatesInTimetable: true,
    showHoursInTimetable: true,
    highlightCurrentTime: true,
    enableLessonDetails: true,
    enablePullToRefresh: true,

    dataCollectionPerformance: navigator.doNotTrack !== '1' && !navigator.globalPrivacyControl,
    dataCollectionCrashes: true,

    themeType: ThemeType.System,
    accentColor: AccentColorName.Green,

    moodleToken: '',
    circularsPassword: '',

    dataVersion: 'Ni podatkov',
  }),

  persist: {
    serializer: {
      deserialize: string => {
        // Load the raw store from local storage
        const deserialized = JSON.parse(string)

        // Validate each type enum value
        deserialized.entityType = validateEnum(EntityType, deserialized.entityType, EntityType.None)
        deserialized.snackType = validateEnum(SnackType, deserialized.snackType, SnackType.Normal)
        deserialized.lunchType = validateEnum(LunchType, deserialized.lunchType, LunchType.Normal)
        deserialized.themeType = validateEnum(ThemeType, deserialized.themeType, ThemeType.System)

        // Validate accent color enum value
        deserialized.accentColor = validateEnum(
          AccentColorName,
          deserialized.accentColor,
          AccentColorName.Green,
        )

        // Validate entity list
        if (!Array.isArray(deserialized.entityList)) deserialized.entityList = []

        // Return the validated store
        return deserialized
      },
      serialize: JSON.stringify,
    },
  },
})
