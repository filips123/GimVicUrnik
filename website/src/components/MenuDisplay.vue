<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useDisplay } from 'vuetify'

import type { LunchSchedule, Menu } from '@/stores/food'
import { useSettingsStore } from '@/stores/settings'
import { localizeDate, localizeDay } from '@/utils/localization'

const props = defineProps<{ menu: Menu; lunchSchedules?: LunchSchedule[] }>()

const { mobile } = useDisplay()

const { snackType, lunchType } = storeToRefs(useSettingsStore())
const snackMenu = computed(() => props.menu?.snack?.[snackType.value])
const lunchMenu = computed(() => props.menu?.lunch?.[lunchType.value])
</script>

<!-- TODO: Create custom theme colors for day card, like grey lighten 3 for light and grey darken 4 for dark -->

<template>
  <v-card v-if="!mobile" :title="localizeDay(menu.date)" :subtitle="localizeDate(menu.date)" />
  <v-card v-if="snackMenu" title="Malica" :text="snackMenu" class="text-pre-line" />
  <v-card v-if="lunchMenu" title="Kosilo" :text="lunchMenu" class="text-pre-line" />
  <v-card v-if="lunchSchedules?.length" title="Razpored kosila">
    <template #text>
      <div
        v-for="lunchSchedule in lunchSchedules"
        :key="lunchSchedule.time + lunchSchedule.class"
        class="pb-2"
      >
        <div v-if="lunchSchedule.time">Ura: {{ lunchSchedule.time }}</div>
        <div v-if="lunchSchedule.location">Prostor: {{ lunchSchedule.location }}</div>
        <div v-if="lunchSchedule.notes">Opombe: {{ lunchSchedule.notes }}</div>
      </div>
    </template>
  </v-card>
</template>
