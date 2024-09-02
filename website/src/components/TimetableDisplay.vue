<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableEmptyClassrooms from '@/components/TimetableEmptyClassrooms.vue'
import TimetableLesson from '@/components/TimetableLesson.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { type MergedLesson, useTimetableStore } from '@/stores/timetable'
import { getCurrentDay } from '@/utils/days'
import { localizedWeekdays } from '@/utils/localization'
import { getCurrentTime, lessonTimes } from '@/utils/times'

const { targetDay } = defineProps<{ targetDay?: number }>()
const daySpecific = computed(() => typeof targetDay !== 'undefined')

const detailsDialog = defineModel<boolean>('detailsDialog')
const detailsProps = defineModel<{ day: number; time: number; lessons: MergedLesson[] }>(
  'detailsProps',
)

const { currentEntityType } = storeToRefs(useSessionStore())
const { lessons } = storeToRefs(useTimetableStore())

const { showHoursInTimetable, highlightCurrentTime, enableLessonDetails } =
  storeToRefs(useSettingsStore())

const isWeekend = [0, 6].includes(new Date().getDay())
const currentDay = getCurrentDay()
const currentTime = getCurrentTime()

/**
 * Determines the range of lesson times that need to be displayed in the timetable.
 *
 * If target day is specified, it filters the lessons based on its value, otherwise,
 * it calculates the result based on all lessons.
 */
const timeInterval = computed(() => {
  const flat = daySpecific.value
    ? lessons.value.map(timeSlot => timeSlot[targetDay!]).flat()
    : lessons.value.flat(2)
  const minTime = flat.reduce((min, lesson) => (lesson.time < min ? lesson.time : min), Infinity)
  const maxTime = flat.reduce((max, lesson) => (lesson?.time > max ? lesson?.time : max), 0)
  return [minTime, maxTime]
})

function lessonStyles(dayIndex: number, timeIndex: number) {
  // prettier-ignore
  return {
    'bg-surface-highlighted': lessons.value[timeIndex][dayIndex]?.find(lesson => lesson.isSubstitution),
    'current-time': highlightCurrentTime.value && !isWeekend && dayIndex === currentDay && timeIndex === currentTime,
  }
}

function handleDetails(dayIndex: number, timeIndex: number, event: Event) {
  if (!enableLessonDetails.value) return
  if ((event.target as HTMLElement)?.tagName === 'A') return

  detailsProps.value = {
    day: dayIndex,
    time: timeIndex,
    lessons: lessons.value?.[timeIndex]?.[dayIndex] || [],
  }

  detailsDialog.value = true
}

function filterForTargetDay(lessonsTime: MergedLesson[][]) {
  if (typeof targetDay !== 'undefined') return [lessonsTime[targetDay]]
  return lessonsTime
}
</script>

<template>
  <v-table-main>
    <thead v-if="!daySpecific">
      <tr class="bg-surface-subtle text-h6">
        <th :colspan="!daySpecific && showHoursInTimetable ? 2 : 1">Ura</th>
        <th
          v-for="(weekday, index) in localizedWeekdays"
          :key="index"
          :class="{ 'bg-surface-medium': index === currentDay && !isWeekend }"
          v-text="weekday"
        />
      </tr>
    </thead>

    <tbody>
      <template v-for="(lessonsTime, timeIndex) in lessons" :key="timeIndex">
        <tr
          v-if="timeIndex >= timeInterval[0] && timeIndex <= timeInterval[1]"
          class="timetable-row"
          :class="daySpecific ? lessonStyles(targetDay!, timeIndex) : undefined"
          :tabindex="daySpecific ? 0 : undefined"
          @click="daySpecific ? handleDetails(targetDay!, timeIndex, $event) : undefined"
          @keydown.enter="daySpecific ? handleDetails(targetDay!, timeIndex, $event) : undefined"
        >
          <td class="time-number" v-text="timeIndex === 0 ? 'PU' : timeIndex + '.'" />
          <td
            v-if="!daySpecific && showHoursInTimetable"
            class="time-range"
            v-text="lessonTimes[timeIndex].join('–')"
          />
          <td
            v-for="(lessonsTimeDay, dayIndex) in filterForTargetDay(lessonsTime)"
            :key="`${timeIndex}-${dayIndex}`"
            :class="!daySpecific ? lessonStyles(dayIndex, timeIndex) : undefined"
            :tabindex="!daySpecific ? 0 : undefined"
            @click="!daySpecific ? handleDetails(dayIndex, timeIndex, $event) : undefined"
            @keydown.enter="!daySpecific ? handleDetails(dayIndex, timeIndex, $event) : undefined"
          >
            <table
              v-if="currentEntityType !== EntityType.EmptyClassrooms"
              role="presentation"
              class="w-100"
            >
              <tr
                v-for="lesson in lessonsTimeDay"
                :key="`${lesson.time}-${lesson.day}-${lesson.class}-${lesson.teacher}-${lesson.classroom}`"
              >
                <TimetableLesson :lesson="lesson" />
              </tr>
            </table>
            <TimetableEmptyClassrooms v-else :lessons="lessonsTimeDay" />
          </td>
        </tr>
      </template>
    </tbody>
  </v-table-main>
</template>

<style>
/* Improve display timetable cells */

.timetable-row > td {
  padding: 0 !important;
}

.time-number {
  width: min(12vw, 5rem);
}

.time-range {
  width: min(12vw, 7rem);
}

/* Add style for current time */

.current-time {
  background-image: repeating-linear-gradient(
    -45deg,
    transparent,
    transparent 20px,
    rgba(var(--v-current-time-color), var(--v-current-time-opacity)) 20px,
    rgba(var(--v-current-time-color), var(--v-current-time-opacity)) 40px
  );
}
</style>
