<script setup lang="ts">
import { computed } from 'vue'

import type { Menu, LunchSchedule } from '@/stores/menu'
import { useSettingsStore, EntityType, LunchType, SnackType } from '@/stores/settings'

const props = defineProps<{
  menu: Menu
  lunchSchedule: LunchSchedule[]
  mobile: boolean
}>()

const settingsStore = useSettingsStore()

// Shorter solution possible??
// Get current snack
const currentSnack = computed(() => {
  if (!props.menu?.snack) return null
  const snackMenu = props.menu.snack

  switch (settingsStore.snackType) {
    case SnackType.Vegetarian:
      return snackMenu.vegetarian
    case SnackType.Poultry:
      return snackMenu.poultry
    case SnackType.Fruitvegetable:
      return snackMenu.fruitvegetable
    default:
      return snackMenu.normal
  }
})

// Get current lunch
const currentLunch = computed(() => {
  if (!props.menu?.lunch) return null
  const lunchMenu = props.menu.lunch

  switch (settingsStore.lunchType) {
    case LunchType.Vegetarian:
      return lunchMenu.vegetarian
    default:
      return lunchMenu.normal
  }
})

// Get current lunch schedule
const currentLunchSchedules = computed(() => {
  if (settingsStore.entityType !== EntityType.Class) return null

  return props.lunchSchedule?.filter((schedule) => schedule.class === settingsStore.class)
})

// Format date to show day name
function formatDay(date: string): string {
  return new Date(date).toLocaleDateString('sl', { weekday: 'long' })
}

// Format date to show slovenian writing convention
function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('sl')
}
</script>

<template>
  <v-card v-if="!mobile" class="menu-display">
    <v-card-title class="text-capitalize">{{ formatDay(menu.date) }}</v-card-title>
    <v-card-text>{{ formatDate(menu.date) }}</v-card-text>
  </v-card>

  <v-card v-if="currentSnack" class="menu-display">
    <v-card-title>Malica</v-card-title>
    <v-card-text>{{ currentSnack }}</v-card-text>
  </v-card>

  <v-card v-if="currentLunch" class="menu-display">
    <v-card-title>Kosilo</v-card-title>
    <v-card-text>{{ currentLunch }}</v-card-text>
  </v-card>

  <v-card v-if="currentLunchSchedules?.length" class="menu-display">
    <v-card-title>Razpored kosila</v-card-title>
    <v-card-text v-for="currentLunchSchedule in currentLunchSchedules">
      <span v-if="currentLunchSchedule?.time"> Ura: {{ currentLunchSchedule.time }}<br /> </span>
      <span v-if="currentLunchSchedule?.location">
        Prostor: {{ currentLunchSchedule.location }}<br />
      </span>
      <span v-if="currentLunchSchedule?.notes">
        Opombe: {{ currentLunchSchedule.notes }}<br />
      </span>
    </v-card-text>
  </v-card>
</template>

<style>
.menu-display {
  margin: 10px;
  white-space: pre-line;
}
</style>
