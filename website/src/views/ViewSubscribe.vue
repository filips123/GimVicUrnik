<script setup lang="ts">
import { storeToRefs } from 'pinia'

import SubscribeDisplay from '@/components/SubscribeDisplay.vue'
import { EntityType, useSettingsStore } from '@/stores/settings'

const { entityList, entityType } = storeToRefs(useSettingsStore())

const apiBase = import.meta.env.VITE_API
const feedUrl = `${apiBase}/feed`
const calendarUrl = `${apiBase}/calendar`
</script>

<template>
  <!-- prettier-ignore -->
  <v-column>
    <div>
      <h2 class="text-h5 pb-1">Viri</h2>
      <SubscribeDisplay label="Okrožnice" :url="`${feedUrl}/circulars.atom`" schema="feed" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${feedUrl}/substitutions.atom`" schema="feed" />
      <SubscribeDisplay label="Jedilniki" :url="`${feedUrl}/menus.atom`" schema="feed" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${feedUrl}/schedules.atom`" schema="feed" />
    </div>
    <div v-if="entityType === EntityType.Class" class="pt-4">
      <h2 class="text-h5 pb-1">Koledarji</h2>
      <SubscribeDisplay label="Urnik & Nadomeščanja" :url="`${calendarUrl}/combined/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Urnik" :url="`${calendarUrl}/timetable/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${calendarUrl}/substitutions/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${calendarUrl}/schedules/${entityList}`" schema="webcal" />
    </div>
  </v-column>
</template>
