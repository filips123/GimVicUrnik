<!-- Component that displays menu -->

<template>
  <v-card tile>
    <div class="grey lighten-4">
      <v-card-title class="pt-1 text-capitalize">{{ formatDay(date) }}</v-card-title>
      <v-card-subtitle class="pb-1">{{ formatDate(date) }}</v-card-subtitle>
    </div>

    <v-card-text class="grey--text text--darken-4 pb-0">
      <h2 class="font-weight-regular pb-2">Malica</h2>
      <p v-html=convertNewlines(menu.snack[getSnackType()]) />
    </v-card-text>

    <v-card-text class="grey--text text--darken-4" :class="{'pb-0': currentEntityValid }">
      <h2 class="font-weight-regular pb-2">Kosilo</h2>
      <p v-html=convertNewlines(menu.lunch[getLunchType()]) />
    </v-card-text>

    <v-card-text v-if="currentEntityValid" class="grey--text text--darken-4 pb-2">
      <h2 class="font-weight-regular pb-2">Razpored kosila</h2>
      <p>
        Ura: {{ currentLunchSchedule.time }}<br />
        Prostor: {{ currentLunchSchedule.location }}<br />
        Opombe: {{ currentLunchSchedule.notes }}<br />
      </p>
    </v-card-text>
  </v-card>
</template>

<style lang="scss">

</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, LunchType, SelectedEntity, SettingsModule, SnackType } from '@/store/modules/settings'
import { LunchSchedule, Menu } from '@/store/modules/storage'

@Component
export default class MenuDisplay extends Vue {
  @Prop() date!: Date

  @Prop() lunchSchedule!: LunchSchedule[]
  @Prop() menu!: Menu

  get currentEntity (): SelectedEntity | null {
    return SettingsModule.selectedEntity
  }

  get currentEntityValid (): boolean {
    return !!this.currentEntity && this.currentEntity.type === EntityType.Class
  }

  get currentLunchSchedule (): LunchSchedule | undefined {
    return this.lunchSchedule.find(schedule => this.currentEntity?.data.includes(schedule.class))
  }

  formatDay (date: string): string {
    return new Date(date).toLocaleDateString('sl', { weekday: 'long' })
  }

  formatDate (date: string): string {
    return new Date(date).toLocaleDateString('sl')
  }

  convertNewlines (text: string): string {
    return text.replace(/\n/g, '<br />')
  }

  getSnackType (): string {
    switch (SettingsModule.selectedMenu?.snack) {
      case SnackType.Vegetarian:
        return 'vegetarian'
      case SnackType.Poultry:
        return 'poultry'
      case SnackType.Fruitvegetable:
        return 'fruitvegetable'
      default:
        return 'normal'
    }
  }

  getLunchType (): string {
    switch (SettingsModule.selectedMenu?.lunch) {
      case LunchType.Vegetarian:
        return 'vegetarian'
      default:
        return 'normal'
    }
  }
}
</script>
