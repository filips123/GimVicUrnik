<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

import MenuDay from '@/components/MenuDay.vue'
import { type LunchSchedule, useMenuStore } from '@/stores/menu'
import { useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

const { mobile } = useDisplay()

const { day } = storeToRefs(useUserStore())
const { entities } = storeToRefs(useSettingsStore())

const menuStore = useMenuStore()
const { menus, lunchSchedules, updateMenus, updateLunchSchedules } = menuStore
updateMenus()
updateLunchSchedules()

function entitiesLunchSchedules(lunchSchedules: LunchSchedule[]) {
  return lunchSchedules?.filter(schedule => entities.value.includes(schedule.class))
}

const isData = menus.flat().length || lunchSchedules.flat(Infinity).length
</script>

<template>
  <template v-if="isData">
    <div v-if="mobile">
      <MenuDay :menu="menus[day]" :lunch-schedules="entitiesLunchSchedules(lunchSchedules[day])" />
    </div>
    <v-row v-else no-gutters>
      <v-col v-for="(menu, dayIndex) in menus" :key="dayIndex">
        <MenuDay :menu="menu" :lunch-schedules="entitiesLunchSchedules(lunchSchedules[dayIndex])" />
      </v-col>
    </v-row>
  </template>
  <template v-else>Podatkov ni bilo mogoče pridobiti.</template>
</template>
