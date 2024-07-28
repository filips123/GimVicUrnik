<script setup lang="ts">
import { storeToRefs } from 'pinia'

import SubscribeDisplay from '@/components/SubscribeDisplay.vue'
import { EntityType, useSettingsStore } from '@/stores/settings'

const { entityList, entityType } = storeToRefs(useSettingsStore()),
  api = import.meta.env.VITE_API,
  feed = `${api}/feed`,
  calendar = `${api}/calendar`
</script>

<!-- TODO: Styling -->

<template>
  <v-column>
    <div>
      <SubscribeDisplay label="Okrožnice" :url="`${feed}/circulars.atom`" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${feed}/substitutions.atom`" />
      <SubscribeDisplay label="Jedilniki" :url="`${feed}/menus.atom`" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${feed}/schedules.atom`" />
    </div>
    <div v-if="entityType === EntityType.Class" class="mt-16">
      <SubscribeDisplay label="Urnik in Nadomeščanja" :url="`${calendar}/combined/${entityList}`" />
      <SubscribeDisplay label="Urnik" :url="`${calendar}/timetable/${entityList}`" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${calendar}/substitutions/${entityList}`" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${calendar}/schedules/${entityList}`" />
    </div>
  </v-column>
</template>
