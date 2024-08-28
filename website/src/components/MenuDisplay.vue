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

<template>
  <v-card-main
    v-if="!mobile"
    :title="localizeDay(menu.date)"
    :subtitle="localizeDate(menu.date)"
    class="bg-surface-subtle"
  />
  <v-card-main v-if="snackMenu" title="Malica" :text="snackMenu" />
  <v-card-main v-if="lunchMenu" title="Kosilo" :text="lunchMenu" />
  <v-card-main v-if="lunchSchedules?.length" title="Razpored kosila">
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
  </v-card-main>
</template>
