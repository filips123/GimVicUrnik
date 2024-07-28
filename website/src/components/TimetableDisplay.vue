<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableLesson from '@/components/TimetableLesson.vue'
import { useSettingsStore } from '@/stores/settings'
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

const { lessonsList, lessonsTensor } = storeToRefs(useTimetableStore())

const { showHoursInTimetable, showSubstitutions, showCurrentTime, enableLessonDetails } =
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
  const lessons = daySpecific.value
    ? lessonsList.value.filter(lesson => lesson.day === targetDay! + 1)
    : lessonsList.value
  const minTime = lessons.reduce((min, lesson) => (lesson.time < min ? lesson.time : min), Infinity)
  const maxTime = lessons.reduce((max, lesson) => (lesson?.time > max ? lesson?.time : max), 0)
  return [minTime, maxTime]
})

function lessonStyles(dayIndex: number, timeIndex: number) {
  return {
    'bg-surface-variation-secondary':
      showSubstitutions.value &&
      lessonsTensor.value[timeIndex][dayIndex]?.find(lesson => lesson.isSubstitution),
    'current-time':
      showCurrentTime.value && !isWeekend && dayIndex === currentDay && timeIndex === currentTime,
  }
}

function handleDetails(dayIndex: number, timeIndex: number, event: Event) {
  if (!enableLessonDetails.value) return
  if ((event.target as HTMLElement)?.tagName === 'A') return

  detailsProps.value = {
    day: dayIndex,
    time: timeIndex,
    lessons: lessonsTensor.value?.[timeIndex]?.[dayIndex] || [],
  }

  detailsDialog.value = true
}

function filterLessons(lessonsTime: MergedLesson[][]) {
  if (typeof targetDay !== 'undefined') return [lessonsTime[targetDay]]
  return lessonsTime
}
</script>

<template>
  <v-table>
    <thead v-if="!daySpecific">
      <tr class="bg-surface-variation">
        <th :colspan="!daySpecific && showHoursInTimetable ? 2 : 1">Ura</th>
        <th
          v-for="(weekday, index) in localizedWeekdays"
          :key="index"
          :class="{ 'bg-primary': index === currentDay && !isWeekend }"
          v-text="weekday"
        />
      </tr>
    </thead>

    <tbody>
      <tr
        v-for="(lessonsTime, timeIndex) in lessonsTensor"
        :key="timeIndex"
        :class="daySpecific ? lessonStyles(targetDay!, timeIndex) : null"
        @click="daySpecific ? handleDetails(targetDay!, timeIndex, $event) : null"
      >
        <template v-if="timeIndex >= timeInterval[0] && timeIndex <= timeInterval[1]">
          <td v-text="timeIndex === 0 ? 'PU' : timeIndex + '.'" />
          <td
            v-if="!daySpecific && showHoursInTimetable"
            v-text="lessonTimes[timeIndex].join('–')"
          />
          <td
            v-for="(lessonsDay, dayIndex) in filterLessons(lessonsTime)"
            :key="`${timeIndex}-${dayIndex}`"
            :class="!daySpecific ? lessonStyles(dayIndex, timeIndex) : null"
            @click="!daySpecific ? handleDetails(dayIndex, timeIndex, $event) : null"
          >
            <table>
              <tr
                v-for="lesson in lessonsDay"
                :key="`${lesson.time}-${lesson.day}-${lesson.class}-${lesson.teacher}-${lesson.classroom}`"
              >
                <TimetableLesson :lesson="lesson" />
              </tr>
            </table>
          </td>
        </template>
      </tr>
    </tbody>
  </v-table>
</template>
