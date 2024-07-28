<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

import MenuDisplay from '@/components/MenuDisplay.vue'
import { type LunchSchedule, useFoodStore } from '@/stores/food'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'

const { mobile } = useDisplay()

const { day } = storeToRefs(useSessionStore())
const { entityList, entityType } = storeToRefs(useSettingsStore())

const foodStore = useFoodStore()
const { menus, lunchSchedules } = storeToRefs(foodStore)
const { updateMenus, updateLunchSchedules } = foodStore

updateMenus()
updateLunchSchedules()

function entitiesLunchSchedules(lunchSchedules?: LunchSchedule[]) {
  if (!lunchSchedules || entityType.value !== EntityType.Class) return []
  return lunchSchedules.filter(schedule => entityList.value.includes(schedule.class))
}

// Stop stopping event propagation on touch handlers
const touchOptions = {
  start: () => {},
  end: () => {},
}
</script>

<template>
  <v-window v-if="mobile" v-model="day" :touch="touchOptions" class="h-100">
    <v-window-item v-for="(menu, dayIndex) in menus" :key="dayIndex" :value="dayIndex">
      <MenuDisplay
        :menu="menu"
        :lunch-schedules="entitiesLunchSchedules(lunchSchedules[dayIndex])"
      />
    </v-window-item>
  </v-window>

  <v-row v-else no-gutters>
    <v-col v-for="(menu, dayIndex) in menus" :key="dayIndex">
      <MenuDisplay
        :menu="menu"
        :lunch-schedules="entitiesLunchSchedules(lunchSchedules[dayIndex])"
      />
    </v-col>
  </v-row>
</template>
