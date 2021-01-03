import { getModule, Module, Mutation, VuexModule } from 'vuex-module-decorators'

import store from '@/store'
import { SelectedEntity, SelectedMenu } from '@/store/modules/settings'
import { getCurrentDay } from '@/utils/days'

@Module({ name: 'state', dynamic: true, store })
class State extends VuexModule {
  currentDay = getCurrentDay()

  currentEntity: SelectedEntity | null = null
  currentMenu: SelectedMenu | null = null

  @Mutation
  setCurrentDay (currentDay: number): void {
    this.currentDay = currentDay
  }

  @Mutation
  setCurrentEntity (currentEntity: SelectedEntity): void {
    this.currentEntity = currentEntity
  }

  @Mutation
  setCurrentMenu (currentMenu: SelectedMenu): void {
    this.currentMenu = currentMenu
  }
}

export const StateModule = getModule(State)
