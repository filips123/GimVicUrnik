import { EntityType, SnackType, LunchType, ThemeType, MenuType } from '@/stores/settings'

// Days localization
export function localizeDay(date: string): string {
  const day = new Date(date).toLocaleDateString('sl', { weekday: 'long' })
  return day.charAt(0).toUpperCase() + day.slice(1)
}

export function localizeDate(date: string): string {
  return new Date(date).toLocaleDateString('sl')
}

export const localizedWeekdays = ['Ponedeljek', 'Torek', 'Sreda', 'Četrtek', 'Petek']

// Entity localization
export function localizeEntityType(entityType: EntityType) {
  switch (entityType) {
    case EntityType.Class:
      return 'razred'
    case EntityType.Teacher:
      return 'profesor'
    case EntityType.Classroom:
    case EntityType.EmptyClassrooms:
      return 'učilnica'
  }
}

// Menu localization
export function localizeSnackType(snackType: SnackType) {
  switch (snackType) {
    case SnackType.Normal:
      return 'Navadna'
    case SnackType.Vegetarian:
      return 'Vegetarijanska'
    case SnackType.Poultry:
      return 'Vegetarijanska s perutnino in ribo'
    case SnackType.Fruitvegetable:
      return 'Sadnozelenjavna'
  }
}

export function localizeLunchType(lunchType: LunchType) {
  switch (lunchType) {
    case LunchType.Normal:
      return 'Navadno'
    case LunchType.Vegetarian:
      return 'Vegetarijansko'
  }
}

export function localizeMenu(menuType: MenuType) {
  switch (menuType) {
    case MenuType.Snack:
      return 'Malica'
    case MenuType.Lunch:
      return 'Kosilo'
  }
}

export const localizedSnackTypeList = [
  'Navadna',
  'Vegetarijanska',
  'Vegetarijanska s perutnino in ribo',
  'Sadnozelenjavna',
]
export const localizedLunchTypeList = ['Navadno', 'Vegetarijansko']

// Settings localization
export function localizeThemeType(themeType: ThemeType) {
  switch (themeType) {
    case ThemeType.System:
      return 'Sistemska'
    case ThemeType.Light:
      return 'Svetla'
    case ThemeType.Dark:
      return 'Temna'
  }
}

export const localizedSwitchSettings = [
  'Prikaži nadomešanja',
  'Prikaži povezave v urniku',
  'Prikaži ure v urniku',
  'Prikaži trenutno uro',
  'Klikni za podrobnosti',
  'Potegni za posodobitev',
  'Samodejno posodabljanje',
]

export const localizedThemeTypeList = ['Sistemska', 'Svetla', 'Temna']
