<script setup lang="ts">
import SubscribeDisplay from '@/components/SubscribeDisplay.vue'
import { EntityType, useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()
const { entities, entityType } = settingsStore

const api = import.meta.env.VITE_API
const feed = `${api}/feed`
const calendar = `${api}/calendar`
</script>

<template>
  <v-column>
    <div>
      <SubscribeDisplay label="Okrožnice" :url="`${feed}/circulars.atom`" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${feed}/substitutions.atom`" />
      <SubscribeDisplay label="Jedilniki" :url="`${feed}/menus.atom`" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${feed}/schedules.atom`" />
    </div>
    <div v-if="entityType === EntityType.Class" class="mt-16">
      <SubscribeDisplay label="Urnik in Nadomeščanja" :url="`${calendar}/combined/${entities}`" />
      <SubscribeDisplay label="Urnik" :url="`${calendar}/timetable/${entities}`" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${calendar}/substitutions/${entities}`" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${calendar}/schedules/${entities}`" />
    </div>
  </v-column>
</template>
