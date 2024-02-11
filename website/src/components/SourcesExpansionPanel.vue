<script setup lang="ts">
import type { Document } from '@/stores/documents'
import { useSettingsStore } from '@/stores/settings'
import { getWeekdays } from '@/utils/days'
import { tokenizeUrl } from '@/utils/documents'
import { localizeDate } from '@/utils/localization'

const props = defineProps<{ documents: Document[]; title: string; dateAsWeek?: boolean }>()

const settingsStore = useSettingsStore()
const { moodleToken } = settingsStore

function displayedDate(document: Document): string {
  if (props.dateAsWeek) {
    const weekdays = getWeekdays(new Date(document.effective))
    return `${localizeDate(weekdays[0].toString())} - ${localizeDate(weekdays[4].toString())}`
  }

  return localizeDate(document.effective)
}
</script>

<template>
  <v-expansion-panels v-if="documents?.length">
    <v-expansion-panel :title>
      <template #text>
        <v-list>
          <v-list-item
            v-for="document in documents"
            :key="document.title"
            :title="document.title"
            :subtitle="displayedDate(document)"
            :href="tokenizeUrl(document.url, moodleToken)"
            target="_blank"
          />
        </v-list>
      </template>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<style>
.v-expansion-panel-text__wrapper {
  padding: 0 0 8px !important;
}
</style>
