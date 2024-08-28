<script setup lang="ts">
import { computed } from 'vue'

import type { MergedLesson } from '@/stores/timetable'
import { getCurrentDate } from '@/utils/days'
import { localizeDate, localizedWeekdays } from '@/utils/localization'
import { lessonTimes } from '@/utils/times'

const dialog = defineModel<boolean>()
const props = defineProps<{ day: number; time: number; lessons: MergedLesson[] }>()

const lessonDay = computed(() => localizedWeekdays[props.day])
const lessonDuration = computed(() => lessonTimes[props.time].join('–'))

const lessonDate = computed(() => {
  const currentDate = getCurrentDate()
  currentDate.setDate(currentDate.getDate() - currentDate.getDay() + props.day + 1)
  return localizeDate(currentDate)
})

const title = computed(() => (props.time ? `${props.time}. ura` : 'Predura'))
const subtitle = computed(() => `${lessonDay.value}, ${lessonDate.value}, ${lessonDuration.value}`)

const substitutions = computed(() => props.lessons.filter(lesson => lesson.isSubstitution))

function displayDifferent(value1: string | null, value2: string | null): string {
  if (!value1) value1 = '/'
  if (!value2) value2 = '/'

  if (value1 === value2) return value1
  return `${value1} → ${value2}`
}
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card :title :subtitle>
      <template v-if="substitutions.length" #text>
        <div
          v-for="(substitution, index) in substitutions"
          :key="index"
          :class="{ 'mb-4': index !== substitutions.length - 1 }"
        >
          <!-- prettier-ignore -->
          <v-list dense class="lesson-details pa-0">
            <v-list-item class="px-0">
              <v-list-item-title>Razred</v-list-item-title>
              <v-list-item-subtitle>{{ substitution.class }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item class="px-0">
              <v-list-item-title>Predmet</v-list-item-title>
              <v-list-item-subtitle>{{ displayDifferent(substitution.subject, substitution.substitutionSubject) }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item class="px-0">
              <v-list-item-title>Profesor</v-list-item-title>
              <v-list-item-subtitle>{{ displayDifferent(substitution.teacher, substitution.substitutionTeacher) }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item class="px-0">
              <v-list-item-title>Učilnica</v-list-item-title>
              <v-list-item-subtitle>{{ displayDifferent(substitution.classroom, substitution.substitutionClassroom) }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item v-if="substitution.notes" class="px-0">
              <v-list-item-title>Opombe</v-list-item-title>
              <v-list-item-subtitle>{{ substitution.notes }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </div>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
/* Improve display of lesson details */

.lesson-details .v-list-item-title {
  max-width: 5rem;
}

.lesson-details .v-list-item-subtitle {
  white-space: break-spaces;
}
</style>
