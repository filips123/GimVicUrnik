<script setup lang="ts">
import type { Document } from '@/stores/documents'

import { getWeekdays } from '@/composables/days'
import { localizeDate } from '@/composables/localization'
import { tokenizeUrl } from '@/composables/documents'

const props = defineProps<{
  documents: Document[]
  title: string
  displayedDate: string
}>()

function displayDate(document: Document): string {
  let date: string

  switch (props.displayedDate) {
    case 'created':
      date = document.created
      break
    case 'modified':
      date = document.modified
      break
    case 'effective':
      date = document.effective
      break
    default:
      return ''
  }

  if (document.type === 'snack-menu' || document.type === 'lunch-menu') {
    const weekdays = getWeekdays(new Date(date))
    return `${localizeDate(weekdays[0].toString())} - ${localizeDate(weekdays[4].toString())}`
  }

  return localizeDate(date)
}
</script>

<template>
  <v-expansion-panels v-if="documents?.length > 0">
    <v-expansion-panel :title="title">
      <v-expansion-panel-text>
        <v-list>
          <v-list-item
            v-for="document in documents"
            :href="tokenizeUrl(document.url)"
            :title="document.title"
            :subtitle="displayDate(document)"
          />
        </v-list>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style>
.v-expansion-panels {
  margin: 16px auto !important;
  max-width: 40rem !important;
}

/* Remove horizontal padding from list */
.v-expansion-panel-text__wrapper {
  padding: 0 0 8px !important;
}

/* Change section title line height and padding*/
.v-expansion-panel-title {
  line-height: 1rem !important;
  min-height: 48px !important;
  padding: 0 16px !important;
}
</style>
