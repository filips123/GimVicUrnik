<script setup lang="ts">
import { computed } from 'vue'
import { useDisplay } from 'vuetify'

import MenuDisplay from '@/components/MenuDisplay.vue'

import { useMenuStore } from '@/stores/menu'
import { useUserStore } from '@/stores/user'

// TODO: Check for tablet
const { mobile } = useDisplay()

document.title = import.meta.env.VITE_TITLE + '- Jedilnik'

const userStore = useUserStore()
const menuStore = useMenuStore()

// Update Menus and lunch schedules
menuStore.updateMenus()
menuStore.updateLunchSchedules()

const { menus, lunchSchedules } = menuStore

// TODO: Menus can be undefined still and don't have the array values sometimes
// Get Menu of the day
const dayMenu = computed(() => {
  return {
    menu: menus[userStore.day],
    lunchSchedule: lunchSchedules[userStore.day]
  }
})
</script>

<template>
  <menu-display
    v-if="mobile"
    :menu="dayMenu.menu"
    :lunch-schedule="dayMenu.lunchSchedule"
    :mobile="mobile" />
  <v-row v-else no-gutters>
    <v-col v-for="(menu, dayIndex) in menus">
      <menu-display :menu="menu" :lunch-schedule="lunchSchedules[dayIndex]" :mobile="mobile" />
    </v-col>
  </v-row>
</template>
