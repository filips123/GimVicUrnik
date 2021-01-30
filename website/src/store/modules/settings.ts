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
  Poultry,
  Vegetarian,
  Fruitvegetable
}

export enum LunchType {
  Normal,
  Vegetarian
}

export interface SelectedEntity {
  type: EntityType;
  data: string[];
}

export interface SelectedMenu {
  snack: SnackType;
  lunch: LunchType;
}

interface NavigatorGPC extends Navigator {
  globalPrivacyControl: boolean | undefined
}

@Module({ name: 'settings', dynamic: true, preserveState: true, preserveStateType: 'mergeReplaceArrays', store })
class Settings extends VuexModule {
  selectedEntity: SelectedEntity | null = null
  selectedMenu: SelectedMenu | null = null

  showSubstitutions = true
  showLinksInTimetable = true
  enablePullToRefresh = true
  showHours = false
  enableUpdateOnLoad = false
  doNotTrack: boolean = navigator.doNotTrack === '1' || !!(navigator as NavigatorGPC).globalPrivacyControl
  darkTheme: boolean | null = null

  @Mutation
  setSelectedEntity (selectedEntity: SelectedEntity): void {
    this.selectedEntity = selectedEntity
  }

  @Mutation
  setSelectedMenu (selectedMenu: SelectedMenu): void {
    this.selectedMenu = selectedMenu
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
  setShowHours (showHours: boolean): void {
    this.showHours = showHours
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
  setDoNotTrack (doNotTrack: boolean): void {
    this.doNotTrack = doNotTrack
  }

  @Mutation
  setDarkTheme (darkTheme: boolean | null): void {
    this.darkTheme = darkTheme
  }
}

export const SettingsModule = getModule(Settings)
