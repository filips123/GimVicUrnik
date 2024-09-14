<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref } from 'vue'
import { useDisplay } from 'vuetify'

import TimetableDetails from '@/components/TimetableDetails.vue'
import TimetableDisplay from '@/components/TimetableDisplay.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType } from '@/stores/settings'
import { type MergedLesson, useTimetableStore } from '@/stores/timetable'
import { localizedWeekdays } from '@/utils/localization'

const { mobile } = useDisplay()

const { currentEntityType, day } = storeToRefs(useSessionStore())
const { updateTimetable, updateSubstitutions, updateEmptyClassrooms } = useTimetableStore()

updateTimetable()
updateSubstitutions()

if (currentEntityType.value === EntityType.EmptyClassrooms) updateEmptyClassrooms()

const detailsDialog = ref(false)
const detailsProps = ref({ day: -1, time: -1, lessons: [] as MergedLesson[] })

// Stop stopping event propagation on touch handlers
const touchOptions = {
  start: () => {},
  end: () => {},
}
</script>

<template>
  <v-window v-if="mobile" v-model="day" :touch="touchOptions" class="h-100">
    <v-window-item v-for="(_, dayIndex) in localizedWeekdays" :key="dayIndex" :value="dayIndex">
      <TimetableDisplay
        v-model:details-dialog="detailsDialog"
        v-model:details-props="detailsProps"
        :target-day="dayIndex"
      />
    </v-window-item>
  </v-window>

  <TimetableDisplay
    v-else
    v-model:details-dialog="detailsDialog"
    v-model:details-props="detailsProps"
  />

  <TimetableDetails v-model="detailsDialog" v-bind="detailsProps" />
</template>
