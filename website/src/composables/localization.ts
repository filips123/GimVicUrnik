import { EntityType, SnackType, LunchType, ThemeType } from '@/stores/settings'

export const localizeSnackTypeList = [
  'Navadna',
  'Vegetarijanska',
  'Vegetarijanska s perutnino in ribo',
  'Sadnozelenjavna'
]
export const localizeLunchTypeList = ['Navadno', 'Vegetarijansko']

export function localizeEntityType(entityType: EntityType) {
  switch (entityType) {
    case EntityType.Class:
      return 'razred'
    case EntityType.Teacher:
      return 'profesor'
    case EntityType.Classroom:
      return 'učilnica'
    case EntityType.EmptyClassrooms:
      return 'prazne učilnice'
  }
}

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

export const localizeSwitchSettings = [
  'Prikaži nadomešanja',
  'Prikaži povezave v urniku',
  'Prikaži ure v urniku',
  'Klikni za podrobnosti',
  'Potegni za posodobitev',
  'Samodejno posodabljanje'
]

export const localizeThemeTypeList = ['Sistemska', 'Svetla', 'Temna']

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
