<script setup lang="ts">
import MenuDay from '@/components/MenuDay.vue'
import { useMenuStore, type LunchSchedule } from '@/stores/menu'
import { useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

const { mobile } = useDisplay()

const { day } = storeToRefs(useUserStore())
const { entities } = storeToRefs(useSettingsStore())

const menuStore = useMenuStore()
const { menus, lunchSchedules, updateMenus, updateLunchSchedules } = menuStore
updateMenus()
updateLunchSchedules()

function entitiesLunchSchedules(lunchSchedules: LunchSchedule[]) {
  return lunchSchedules?.filter((schedule) => entities.value.includes(schedule.class))
}
</script>

<template>
  <div v-if="mobile">
    <MenuDay :menu="menus[day]" :lunch-schedules="entitiesLunchSchedules(lunchSchedules[day])" />
  </div>
  <v-row v-else no-gutters>
    <v-col v-for="(menu, dayIndex) in menus" :key="dayIndex">
      <MenuDay :menu="menu" :lunch-schedules="entitiesLunchSchedules(lunchSchedules[dayIndex])" />
    </v-col>
  </v-row>
</template>
