<script setup lang="ts">
import { storeToRefs } from 'pinia'

import type { Document } from '@/stores/documents'
import { useSettingsStore } from '@/stores/settings'
import { getWeekdays } from '@/utils/days'
import { tokenizeUrl } from '@/utils/documents'
import { localizeDate } from '@/utils/localization'

const props = defineProps<{ documents: Document[]; title: string; dateAsWeek?: boolean }>()

const { moodleToken } = storeToRefs(useSettingsStore())

function displayedDate(document: Document): string {
  if (props.dateAsWeek) {
    const weekdays = getWeekdays(new Date(document.effective))
    return `${localizeDate(weekdays[0].toString())} – ${localizeDate(weekdays[4].toString())}`
  }

  return localizeDate(document.effective)
}
</script>

<template>
  <v-expansion-panels v-if="documents?.length" class="sources-panel mb-4">
    <v-expansion-panel>
      <template #title>
        <span class="text-h6">{{ title }}</span>
      </template>
      <template #text>
        <v-list :aria-label="title">
          <v-lazy v-for="document in documents" :key="document.url" height="48">
            <v-list-item
              :title="document.title"
              :subtitle="displayedDate(document)"
              :href="tokenizeUrl(document.url, moodleToken)"
              target="_blank"
            />
          </v-lazy>
        </v-list>
      </template>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style>
/* Prevent expanding title height */

.sources-panel .v-expansion-panel-title {
  min-height: 48px !important;
  padding: 0 24px !important;
}

.sources-panel .v-expansion-panel-text__wrapper {
  padding: 0 0 8px !important;
}
</style>
