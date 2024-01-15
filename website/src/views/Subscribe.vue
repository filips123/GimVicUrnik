<script setup lang="ts">
import { EntityType, useSettingsStore } from '@/stores/settings'

import SubscribeUrl from '@/components/SubscribeUrl.vue'

document.title = import.meta.env.VITE_TITLE + ' - Naročanje'

const api = import.meta.env.VITE_API

const settingsStore = useSettingsStore()
const { entities, entityType } = settingsStore
</script>

<template>
  <div class="pt-4 mx-auto" style="max-width: 35rem">
    <div>
      <SubscribeUrl label="Okrožnice" :url="`${api}/feed/circulars.atom`" />
      <SubscribeUrl label="Nadomeščanja" :url="`${api}/feed/substitutions.atom`" />
      <SubscribeUrl label="Jedilniki" :url="`${api}/feed/menus.atom`" />
      <SubscribeUrl label="Razporedi kosila" :url="`${api}/feed/schedules.atom`" />
    </div>
    <div v-if="entityType === EntityType.Class" class="mt-16">
      <SubscribeUrl label="Urnik in Nadomeščanja" :url="`${api}/calendar/combined/${entities}`" />
      <SubscribeUrl label="Urnik" :url="`${api}/calendar/timetable/${entities}`" />
      <SubscribeUrl label="Nadomeščanja" :url="`${api}/calendar/substitutions/${entities}`" />
      <SubscribeUrl label="Razporedi kosila" :url="`${api}/calendar/schedules/${entities}`" />
    </div>
  </div>
</template>
