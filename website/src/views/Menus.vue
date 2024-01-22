<script setup lang="ts">
import { useDisplay } from 'vuetify'

import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

import { useMenuStore } from '@/stores/menu'

import MenuDisplay from '@/components/MenuDisplay.vue'

document.title = import.meta.env.VITE_TITLE + ' - Jedilnik'

const { mobile } = useDisplay()

const { day } = storeToRefs(useUserStore())

const menuStore = useMenuStore()

menuStore.updateMenus()
menuStore.updateLunchSchedules()

const { menus, lunchSchedules } = menuStore

function swipe(direction: string) {
  switch (direction) {
    case 'left':
      day.value = Math.min(4, day.value + 1)
      break
    case 'right':
      day.value = Math.max(0, day.value - 1)
      break
  }
}
</script>

<template>
  <div
    v-if="mobile"
    v-touch="{
      left: () => swipe('left'),
      right: () => swipe('right'),
    }"
    class="h-auto"
  >
    <MenuDisplay :menu="menus[day]" :lunch-schedules="lunchSchedules[day]" />
  </div>
  <v-row v-else no-gutters>
    <v-col v-for="(menu, dayIndex) in menus">
      <MenuDisplay :menu="menu" :lunch-schedules="lunchSchedules[dayIndex]" />
    </v-col>
  </v-row>
</template>
