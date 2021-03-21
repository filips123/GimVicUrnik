<!-- Component that displays menu and lunch schedule -->

<template>
  <v-card class="menu-display" elevation="2" tile>
    <div v-if="!mobile" :class="{ 'lighten-4': !$vuetify.theme.dark, 'darken-4': $vuetify.theme.dark }" class="grey">
      <v-card-title class="pt-1 text-capitalize">{{ formatDay(date) }}</v-card-title>
      <v-card-subtitle class="pb-1">{{ formatDate(date) }}</v-card-subtitle>
    </div>

    <v-card-text v-if="menu.snack"
      :class="{ 'pb-0': menu.lunch, 'text--darken-4': !$vuetify.theme.dark, 'text--lighten-4': $vuetify.theme.dark }"
      class="grey--text">
      <h2 class="font-weight-regular pb-2">Malica</h2>
      <p v-html=convertNewlines(menu.snack[getSnackType()]) />
    </v-card-text>

    <v-card-text v-if="menu.lunch"
      :class="{ 'pb-0': currentEntityValid && currentLunchSchedules, 'text--darken-4': !$vuetify.theme.dark, 'text--lighten-4': $vuetify.theme.dark }"
      class="grey--text">
      <h2 class="font-weight-regular pb-2">Kosilo</h2>
      <p v-html=convertNewlines(menu.lunch[getLunchType()]) />
    </v-card-text>

    <v-card-text v-if="currentEntityValid && currentLunchSchedules"
      :class="{ 'text--darken-4': !$vuetify.theme.dark, 'text--lighten-4': $vuetify.theme.dark }"
      class="grey--text pb-2">
      <h2 class="font-weight-regular pb-2">Razpored kosila</h2>
      <p v-for="currentLunchSchedule in currentLunchSchedules" :key="currentLunchSchedule.time">
        Ura: {{ currentLunchSchedule.time }}<br />
        Prostor: {{ currentLunchSchedule.location }}<br />
        Opombe: {{ currentLunchSchedule.notes }}<br />
      </p>
    </v-card-text>
  </v-card>
</template>

<style lang="scss">
// Use the same height for all cards
.menu-display {
  height: 100%;
}
</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, LunchType, SelectedEntity, SettingsModule, SnackType } from '@/store/modules/settings'
import { LunchSchedule, Menu } from '@/store/modules/storage'

@Component
export default class MenuDisplay extends Vue {
  @Prop({ default: false }) mobile!: boolean
  @Prop() date!: string

  @Prop() lunchSchedule!: LunchSchedule[]
  @Prop() menu!: Menu

  get currentEntity (): SelectedEntity | null {
    return SettingsModule.selectedEntity
  }

  get currentEntityValid (): boolean {
    return !!this.currentEntity && this.currentEntity.type === EntityType.Class
  }

  get currentLunchSchedules (): LunchSchedule[] | null {
    const lunchSchedules = this.lunchSchedule.filter(schedule => this.currentEntity?.data.includes(schedule.class))
    return lunchSchedules.length ? lunchSchedules : null
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
