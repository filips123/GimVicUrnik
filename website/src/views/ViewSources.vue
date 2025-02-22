<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import SourcesExpansionPanel from '@/components/SourcesExpansionPanel.vue'
import SubscribeDisplay from '@/components/SubscribeDisplay.vue'
import { useDocumentsStore } from '@/stores/documents'
import { EntityType, useSettingsStore } from '@/stores/settings'

const { filterDocuments, updateDocuments } = useDocumentsStore()
const { entityList, entityType } = storeToRefs(useSettingsStore())

updateDocuments()

const substitutions = computed(() => filterDocuments(['substitutions']))
const lunchSchedules = computed(() => filterDocuments(['lunch-schedule']))
const menus = computed(() => filterDocuments(['snack-menu', 'lunch-menu']))

const apiBase = import.meta.env.VITE_API
const feedUrl = `${apiBase}/feed`
const calendarUrl = `${apiBase}/calendar`
</script>

<template>
  <v-column>
    <SourcesExpansionPanel title="Nadomeščanja" :documents="substitutions" />
    <SourcesExpansionPanel title="Razporedi kosila" :documents="lunchSchedules" />
    <SourcesExpansionPanel title="Jedilniki" :documents="menus" date-as-week />

    <v-divider-settings />

    <div>
      <SubscribeDisplay label="Okrožnice" :url="`${feedUrl}/circulars.atom`" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${feedUrl}/substitutions.atom`" />
      <SubscribeDisplay label="Jedilniki" :url="`${feedUrl}/menus.atom`" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${feedUrl}/schedules.atom`" />
    </div>

    <v-divider-settings />

    <!-- prettier-ignore -->
    <div v-if="entityType === EntityType.Class">
      <h2 class="text-h5 pb-1">Koledarji</h2>
      <SubscribeDisplay label="Urnik & Nadomeščanja" :url="`${calendarUrl}/combined/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Urnik" :url="`${calendarUrl}/timetable/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Nadomeščanja" :url="`${calendarUrl}/substitutions/${entityList}`" schema="webcal" />
      <SubscribeDisplay label="Razporedi kosila" :url="`${calendarUrl}/schedules/${entityList}`" schema="webcal" />
    </div>
  </v-column>
</template>
