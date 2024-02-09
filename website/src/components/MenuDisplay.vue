<script setup lang="ts">
import { computed } from 'vue'

import { useDisplay } from 'vuetify'

import type { Menu, LunchSchedule } from '@/stores/menu'
import { useSettingsStore, EntityType } from '@/stores/settings'

import { localizeDay, localizeDate } from '@/composables/localization'

const props = defineProps<{
  menu: Menu
  lunchSchedules: LunchSchedule[]
}>()

const { mobile } = useDisplay()

const settingsStore = useSettingsStore()
const { snackType, lunchType, entities, entityType } = settingsStore

const snackMenu = computed(() => props.menu?.snack?.[snackType])
const lunchMenu = computed(() => props.menu?.lunch?.[lunchType])

const classLunchSchedules = computed(() => {
  if (entityType !== EntityType.Class) return null
  return props.lunchSchedules?.filter((schedule) => entities.includes(schedule.class))
})
</script>

<template>
  <v-card v-if="!mobile" :title="localizeDay(menu.date)" :subtitle="localizeDate(menu.date)" />
  <v-card v-if="snackMenu" title="Malica" :text="snackMenu" />
  <v-card v-if="lunchMenu" title="Kosilo" :text="lunchMenu" />
  <v-card v-if="classLunchSchedules?.length" title="Razpored kosila">
    <v-card-text>
      <div v-for="classLunchSchedule in classLunchSchedules" class="pb-2">
        <div v-if="classLunchSchedule.time">Ura: {{ classLunchSchedule.time }}</div>
        <div v-if="classLunchSchedule?.location">Prostor: {{ classLunchSchedule.location }}</div>
        <div v-if="classLunchSchedule?.notes">Opombe: {{ classLunchSchedule.notes }}</div>
      </div>
    </v-card-text>
  </v-card>
</template>
