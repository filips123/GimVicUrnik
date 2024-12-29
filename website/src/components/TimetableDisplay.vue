<script setup lang="ts">
import { useIntervalFn } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'

import TimetableEmptyClassrooms from '@/components/TimetableEmptyClassrooms.vue'
import TimetableLesson from '@/components/TimetableLesson.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { type MergedLesson, useTimetableStore } from '@/stores/timetable'
import { getCurrentDate, getCurrentDay, getIsWeekend, getWeekdays } from '@/utils/days'
import { localizeDate, localizeDay } from '@/utils/localization'
import { getCurrentTime, lessonTimes } from '@/utils/times'

const { targetDay } = defineProps<{ targetDay?: number }>()
const daySpecific = computed(() => typeof targetDay !== 'undefined')

const detailsDialog = defineModel<boolean>('detailsDialog')
const detailsProps = defineModel<{ day: number; time: number; lessons: MergedLesson[] }>(
  'detailsProps',
)

const { currentEntityType } = storeToRefs(useSessionStore())
const { lessons } = storeToRefs(useTimetableStore())

const { showDatesInTimetable, showHoursInTimetable, highlightCurrentTime, enableLessonDetails } =
  storeToRefs(useSettingsStore())

const isWeekend = ref(getIsWeekend())
const currentDay = ref(getCurrentDay())
const currentTime = ref(getCurrentTime())

useIntervalFn(() => {
  isWeekend.value = getIsWeekend()
  currentDay.value = getCurrentDay()
  currentTime.value = getCurrentTime()
}, 30000)

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
    'current-time': highlightCurrentTime.value && !isWeekend.value && dayIndex === currentDay.value && timeIndex === currentTime.value,
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

function handleSubstitutionsSpecialCase(lessonsTimeDay: MergedLesson[]) {
  // Important: This can cause breaking changes when multiple entities have overlapping times

  // Special cases occur only when multiple lessons happen at the same time in the class view
  // This accounts for ŠVM/ŠVŽ, INFV/INF and language lessons happening at the same time (FRA/ITA/NEM/ŠPA)
  if (currentEntityType.value === EntityType.Class && lessonsTimeDay.length > 1) {
    // If subjects that are not in the timetable originally appear, we replace the original subjects with them
    if (lessonsTimeDay.find(l => l.subject === null)) {
      return lessonsTimeDay.filter(l => l.subject === null)
    }

    // A subject change needs to be present as this is the breaking point
    const lesson: MergedLesson | undefined = lessonsTimeDay.find(
      l => l.isSubstitution && l.substitutionSubject !== l.subject,
    )

    if (!lesson) return lessonsTimeDay

    // We need to treat ŠVM/ŠVŽ and INFV/INF as the same subject, so that what happens to one also happens to another
    if (['ŠVM', 'ŠVŽ', 'INFV', 'INF'].includes(lesson.subject!)) {
      if (lessonsTimeDay.length > 2) {
        // When there are more than two subjects, it means a new subject has appeared
        // We then need to delete the original subjects
        return lessonsTimeDay.filter(l => !['ŠVM', 'ŠVŽ', 'INFV', 'INF'].includes(l.subject || ''))
      } else {
        // We keep only the element of the subject pair that changed
        return lessonsTimeDay.filter(l => l === lesson)
      }
    }

    // At this point we are left only with languages
    const LanguageLesson: MergedLesson | undefined = lessonsTimeDay.find(
      l => l.isSubstitution && !['FRA', 'ITA', 'NEM', 'ŠPA', null].includes(l.substitutionSubject),
    )

    if (!LanguageLesson) return lessonsTimeDay

    // If a subject was changed for another, then all the languages are substituted with the new subject
    return [LanguageLesson!]
  }

  return lessonsTimeDay
}
</script>

<template>
  <v-table-main>
    <thead v-if="!daySpecific">
      <tr class="bg-surface-subtle">
        <th :colspan="showHoursInTimetable ? 2 : 1" class="text-h6">Ura</th>
        <th
          v-for="(date, index) in getWeekdays(getCurrentDate())"
          :key="index"
          :class="{
            'bg-surface-medium': index === currentDay && !isWeekend,
            'py-1': showDatesInTimetable,
          }"
        >
          <span class="text-h6">{{ localizeDay(date) }}</span>
          <div v-if="showDatesInTimetable" class="pb-1 opacity-70">{{ localizeDate(date) }}</div>
        </th>
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
                v-for="lesson in handleSubstitutionsSpecialCase(lessonsTimeDay)"
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
