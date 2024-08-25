import { EntityType, LunchType, MenuType, SnackType, ThemeType } from '@/stores/settings'

// Day Localization

export function localizeDay(date: string | Date): string {
  const day = new Date(date).toLocaleDateString('sl', { weekday: 'long' })
  return day.charAt(0).toUpperCase() + day.slice(1)
}

export function localizeDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('sl')
}

export const localizedWeekdays = ['Ponedeljek', 'Torek', 'Sreda', 'Četrtek', 'Petek']

// Entity Localization

export function localizeEntityLabel(entityType: EntityType) {
  switch (entityType) {
    case EntityType.Class:
    case EntityType.None:
      return 'Razred'
    case EntityType.Teacher:
      return 'Profesor'
    case EntityType.Classroom:
    case EntityType.EmptyClassrooms:
      return 'Učilnica'
  }
}

export function localizeSelectEntityTitle(entityType: EntityType) {
  switch (entityType) {
    case EntityType.Class:
    case EntityType.None:
      return 'Izberite razred'
    case EntityType.Teacher:
      return 'Izberite profesorje'
    case EntityType.Classroom:
    case EntityType.EmptyClassrooms:
      return 'Izberite učilnice'
  }
}

export function localizeSelectEntityNotSelected(entityType: EntityType) {
  switch (entityType) {
    case EntityType.Class:
    case EntityType.None:
      return 'Ni izbranega razreda'
    case EntityType.Teacher:
      return 'Ni izbranega profesorja'
    case EntityType.Classroom:
    case EntityType.EmptyClassrooms:
      return 'Ni izbrane učilnice'
  }
}

// Menu Localization

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

// Settings Localization

export function localizeDataCollection(performance: boolean, crashes: boolean) {
  if (performance && crashes) {
    return 'Merjenje učinkovitosti & Zbiranje napak'
  } else if (performance) {
    return 'Merjenje učinkovitosti'
  } else if (crashes) {
    return 'Zbiranje napak'
  } else {
    return 'Izklopljeno'
  }
}

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
