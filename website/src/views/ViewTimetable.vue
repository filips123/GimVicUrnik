<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'
import { useDisplay } from 'vuetify'

import TimetableDetails from '@/components/TimetableDetails.vue'
import TimetableLesson from '@/components/TimetableLesson.vue'
import { useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'
import { useTimetableStore } from '@/stores/timetable'
import { useUserStore } from '@/stores/user'
import { getCurrentDay } from '@/utils/days'
import { localizedWeekdays } from '@/utils/localization'
import { getCurrentTime, lessonTimes } from '@/utils/times'

const { mobile } = useDisplay()

const { day } = storeToRefs(useUserStore())

const timetableStore = useTimetableStore()
timetableStore.updateTimetable()
timetableStore.updateSubstitutions()
timetableStore.updateEmptyClassrooms()

const settingsStore = useSettingsStore()
const { showHoursInTimetable, showSubstitutions, showCurrentTime, enableShowingDetails } =
  settingsStore

const lessonDetailsDialog = ref(false)
const lessonsDetails = ref([] as MergedLesson[])

const timeInterval = computed(() => {
  const lessons = !mobile.value
    ? timetableStore.lessons
    : timetableStore.lessons.filter(lesson => lesson.day == day.value + 1)
  return [
    lessons.reduce((minTime, lesson) => (lesson.time < minTime ? lesson.time : minTime), 10),
    lessons.reduce((maxTime, lesson) => (lesson?.time > maxTime ? lesson?.time : maxTime), 0),
  ]
})

const lessonsArray = computed(() => {
  const days = 5
  const times = 10

  let lessonsArray: MergedLesson[][][] = Array.from(Array(times), () => new Array(days).fill([]))

  for (const lesson of timetableStore.lessons) {
    lessonsArray[lesson.time][lesson.day - 1] =
      lessonsArray[lesson.time][lesson.day - 1].concat(lesson)
  }

  return lessonsArray
})

function handleDetails(lessons: MergedLesson[], event: Event) {
  if (
    !enableShowingDetails ||
    (event?.target as HTMLInputElement)?.classList.contains('text-primary-variant')
  )
    return

  if (lessons.length) {
    lessonsDetails.value = lessons
    lessonDetailsDialog.value = true
  }
}

function getLessonsDay(lessonsTime: MergedLesson[][]) {
  if (mobile.value) return [lessonsTime[day.value]]
  return lessonsTime
}

const isWeekday = new Date().getDay() in [0, 6]
const currentDay = getCurrentDay()
const currentTime = getCurrentTime()

function styleDesktop(dayIndex: number, timeIndex: number) {
  if (mobile.value) return
  return {
    'bg-surface-variation-secundary':
      showSubstitutions &&
      lessonsArray.value[timeIndex][dayIndex]?.find(lesson => lesson.substitution),
    'current-time':
      showCurrentTime && !isWeekday && timeIndex === currentTime && dayIndex === currentDay,
  }
}

function styleMobile(timeIndex: number) {
  if (!mobile.value) return
  return {
    'bg-surface-variation-secundary':
      showSubstitutions &&
      lessonsArray.value[timeIndex][day.value]?.find(lesson => lesson.substitution),
    'current-time':
      showCurrentTime && !isWeekday && day.value === currentDay && timeIndex === currentTime,
  }
}

const isData = lessonsArray.value.flat(Infinity).length
</script>

<template>
  <v-table v-if="isData">
    <thead>
      <tr v-if="!mobile" class="bg-surface-variation">
        <th :colspan="showHoursInTimetable ? 2 : 1">Ura</th>
        <th
          v-for="(weekday, index) in localizedWeekdays"
          :key="index"
          :class="{ 'bg-primary': index === currentDay && !isWeekday }"
          v-text="weekday"
        ></th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(lessonsTime, timeIndex) in lessonsArray"
        :key="timeIndex"
        :class="styleMobile(timeIndex)"
        @click="mobile ? handleDetails(lessonsArray[timeIndex][day], $event) : null"
      >
        <template v-if="timeIndex >= timeInterval[0] && timeIndex <= timeInterval[1]">
          <td v-text="timeIndex === 0 ? 'PU' : timeIndex + '.'"></td>
          <template v-if="!mobile">
            <td v-if="showHoursInTimetable" v-text="lessonTimes[timeIndex].join(' - ')"></td>
          </template>
          <td
            v-for="(lessonsDay, dayIndex) in getLessonsDay(lessonsTime)"
            :key="timeIndex + '' + dayIndex"
            :class="styleDesktop(dayIndex, timeIndex)"
            @click="!mobile ? handleDetails(lessonsArray[timeIndex][dayIndex], $event) : null"
          >
            <tr
              v-for="lesson in lessonsDay"
              :key="lesson.day + lesson.class + lesson.teacher + lesson.classroom + lesson.time"
              class="d-flex justify-space-between"
            >
              <TimetableLesson :lesson="lesson" />
            </tr>
          </td>
        </template>
      </tr>
    </tbody>
  </v-table>
  <template v-else>Podatkov ni bilo mogoče pridobiti.</template>
  <TimetableDetails v-model="lessonDetailsDialog" :lessons="lessonsDetails" />
</template>

<style>
.current-time {
  background: repeating-linear-gradient(
    -45deg,
    rgba(255, 0, 0, 0),
    rgba(255, 0, 0, 0) 20px,
    rgba(var(--v-theme-current-time), var(--v-current-time-opacity)) 20px,
    rgba(var(--v-theme-current-time), var(--v-current-time-opacity)) 40px
  );
}
</style>
