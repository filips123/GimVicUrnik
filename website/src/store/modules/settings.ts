import { getModule, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import store from '@/store'

export enum EntityType {
  Class,
  Teacher,
  Classroom,
  EmptyClassrooms
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

export enum ThemeType {
  System,
  Light,
  Dark
}

export interface SelectedEntity {
  type: EntityType;
  data: string[];
}

export interface SelectedMenu {
  snack: SnackType;
  lunch: LunchType;
}

export interface DataCollectionConfig {
  performance: boolean;
  crashes: boolean;
}

interface NavigatorGPC extends Navigator {
  globalPrivacyControl: boolean | undefined
}

@Module({ name: 'settings', dynamic: true, preserveState: true, preserveStateType: 'mergeReplaceArrays', store })
class Settings extends VuexModule {
  selectedEntity: SelectedEntity | null = null

  selectedMenu: SelectedMenu = {
    snack: SnackType.Normal,
    lunch: LunchType.Normal
  }

  showSubstitutions = true
  showLinksInTimetable = true
  showHoursInTimetable = true
  enablePullToRefresh = true
  enableUpdateOnLoad = true

  dataCollection: DataCollectionConfig = {
    performance: !(navigator.doNotTrack === '1' || !!(navigator as NavigatorGPC).globalPrivacyControl),
    crashes: true
  }

  theme: ThemeType = ThemeType.System

  @Mutation
  setSelectedEntity (selectedEntity: SelectedEntity): void {
    this.selectedEntity = selectedEntity
  }

  @Mutation
  setSelectedMenu (selectedMenu: SelectedMenu): void {
    this.selectedMenu = selectedMenu
  }

  @Mutation
  setSelectedMenuSnack (snack: SnackType) {
    if (this.selectedMenu === null) this.selectedMenu = { snack, lunch: LunchType.Normal }
    else this.selectedMenu.snack = snack
  }

  @Mutation
  setSelectedMenuLunch (lunch: LunchType) {
    if (this.selectedMenu === null) this.selectedMenu = { snack: SnackType.Normal, lunch }
    else this.selectedMenu.lunch = lunch
  }

  @Mutation
  setShowSubstitutions (showSubstitutions: boolean): void {
    this.showSubstitutions = showSubstitutions
  }

  @Mutation
  setShowLinksInTimetable (showLinksInTimetable: boolean): void {
    this.showLinksInTimetable = showLinksInTimetable
  }

  @Mutation
  setShowHoursInTimetable (showHoursInTimetable: boolean): void {
    this.showHoursInTimetable = showHoursInTimetable
  }

  @Mutation
  setEnablePullToRefresh (enablePullToRefresh: boolean): void {
    this.enablePullToRefresh = enablePullToRefresh
  }

  @Mutation
  setEnableUpdateOnLoad (enableUpdateOnLoad: boolean): void {
    this.enableUpdateOnLoad = enableUpdateOnLoad
  }

  @Mutation
  setDataCollection (dataCollection: DataCollectionConfig): void {
    this.dataCollection = dataCollection
  }

  @Mutation
  setDataCollectionPerformance (performance: boolean): void {
    this.dataCollection.performance = performance
  }

  @Mutation
  setDataCollectionCrashes (crashes: boolean): void {
    this.dataCollection.crashes = crashes
  }

  @Mutation
  setTheme (theme: ThemeType): void {
    this.theme = theme
  }
}

export const SettingsModule = getModule(Settings)
