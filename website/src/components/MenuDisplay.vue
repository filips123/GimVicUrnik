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
  <v-card
    v-if="!mobile"
    class="ma-2"
    :title="localizeDay(menu.date)"
    :text="localizeDate(menu.date)"
  />
  <v-card v-if="snackMenu" class="ma-2 pre-line" title="Malica" :text="snackMenu" />
  <v-card v-if="lunchMenu" class="ma-2 pre-line" title="Kosilo" :text="lunchMenu" />

  <v-card v-if="classLunchSchedules?.length" class="ma-2 pre-line" title="Razpored kosila">
    <v-card-text v-for="classLunchSchedule in classLunchSchedules">
      <span v-if="classLunchSchedule.time">Ura: {{ classLunchSchedule.time }}</span> <br />
      <span v-if="classLunchSchedule?.location"> Prostor: {{ classLunchSchedule.location }} </span>
      <br />
      <span v-if="classLunchSchedule?.notes"> Opombe: {{ classLunchSchedule.notes }} </span><br />
    </v-card-text>
  </v-card>
</template>

<style>
/* Consider new lines */
.pre-line {
  white-space: pre-line;
}
</style>
