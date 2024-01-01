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
</script>

<template>
  <MenuDisplay v-if="mobile" :menu="menus[day]" :lunch-schedules="lunchSchedules[day]" />
  <v-row v-else no-gutters>
    <v-col v-for="(menu, dayIndex) in menus">
      <MenuDisplay :menu="menu" :lunch-schedules="lunchSchedules[dayIndex]" />
    </v-col>
  </v-row>
</template>
