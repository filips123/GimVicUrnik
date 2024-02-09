<script setup lang="ts">
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

import { type MergedLesson, useTimetableStore } from '@/stores/timetable'
import { useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

import { lessonTimes, getCurrentTime } from '@/composables/times'
import { getCurrentDay } from '@/composables/days'
import { localizedWeekdays } from '@/composables/localization'

import TimetableLesson from '@/components/TimetableLesson.vue'
import TimetableDetails from '@/components/TimetableDetails.vue'

const { mobile } = useDisplay()

const timetableStore = useTimetableStore()
const settingsStore = useSettingsStore()

timetableStore.updateTimetable()
timetableStore.updateSubstitutions()
timetableStore.updateEmptyClassrooms()

const { day } = storeToRefs(useUserStore())
const { showHoursInTimetable, showSubstitutions, showCurrentTime, enableShowingDetails } =
  settingsStore

const lessonDetailsDialog = ref(false)

const currentDay = computed(() => getCurrentDay())
const currentTime = computed(() => getCurrentTime())

const maxLessonTime = computed(() => {
  const lessons = !mobile.value
    ? timetableStore.lessons
    : timetableStore.lessons.filter((lesson) => lesson.day == day.value + 1)
  return lessons.reduce(
    (maxTime, lesson) => (lesson?.time > maxTime ? lesson?.time : maxTime),
    lessons[0]?.time,
  )
})

const minLessonTime = computed(() => {
  const lessons = !mobile.value
    ? timetableStore.lessons
    : timetableStore.lessons.filter((lesson) => lesson.day == day.value + 1)
  return lessons.reduce(
    (minTime, lesson) => (lesson.time < minTime ? lesson.time : minTime),
    lessons[0]?.time,
  )
})

const lessonsArray = computed(() => {
  const lessons = timetableStore.lessons

  const days = 6
  const times = 10

  let lessonsArray: MergedLesson[][][] = Array.from(Array(days), () => new Array(times).fill([]))

  for (const lesson of lessons) {
    lessonsArray[lesson.day][lesson.time] = lessonsArray[lesson.day][lesson.time].concat(lesson)
  }

  return lessonsArray
})

const lessonsDetails = ref([] as MergedLesson[])

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

// Class bindings
function styleMobile(timeIndex: number) {
  return {
    'bg-surface-variation-secundary':
      mobile.value &&
      showSubstitutions &&
      lessonsArray.value[day.value + 1][timeIndex]?.find((lesson) => lesson.substitution),
  }
}

import { useTheme } from 'vuetify'

const theme = useTheme()

theme.global.current.value.dark

function styleDesktop(dayIndex: number, timeIndex: number) {
  return {
    'bg-surface-variation-secundary':
      !mobile.value &&
      showSubstitutions &&
      lessonsArray.value[dayIndex][timeIndex].find((lesson) => lesson.substitution),
    'bg-surface-variation': !mobile.value && dayIndex - 1 === currentDay.value,
    'current-time':
      showCurrentTime &&
      !mobile.value &&
      dayIndex - 1 === currentDay.value &&
      timeIndex === currentTime.value,
  }
}

function styleMobileCurrentTime(timeIndex: number) {
  return {
    'current-time':
      showCurrentTime &&
      mobile.value &&
      day.value === currentDay.value &&
      timeIndex === currentTime.value,
  }
}

function swipe(direction: string) {
  if (!mobile.value) return

  switch (direction) {
    case 'left':
      day.value = Math.min(4, day.value + 1)
      break
    case 'right':
      day.value = Math.max(0, day.value - 1)
      break
  }
}
</script>
<template>
  <div
    v-touch="{
      left: () => swipe('left'),
      right: () => swipe('right'),
    }"
    class="touch"
  >
    <v-table>
      <thead>
        <tr v-if="!mobile" class="bg-surface-variation">
          <th :colspan="showHoursInTimetable ? 2 : 1">Ura</th>
          <th
            v-for="(weekday, index) in localizedWeekdays"
            :key="index"
            :class="{ 'bg-primary': index === getCurrentDay() }"
          >
            {{ weekday }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="timeIndex in maxLessonTime"
          :key="timeIndex"
          :class="styleMobile(timeIndex)"
          @click="mobile ? handleDetails(lessonsArray[day + 1][timeIndex], $event) : null"
        >
          <template v-if="timeIndex >= minLessonTime">
            <td :class="styleMobileCurrentTime(timeIndex)">
              {{ timeIndex === 0 ? 'Predura' : timeIndex + '.' }}
            </td>
            <template v-if="!mobile">
              <td v-if="showHoursInTimetable">
                {{ lessonTimes[timeIndex][0] }} - {{ lessonTimes[timeIndex][1] }}
              </td>
            </template>
            <td
              v-for="dayIndex in mobile ? 1 : 5"
              :key="dayIndex"
              :class="styleDesktop(dayIndex, timeIndex)"
              @click="!mobile ? handleDetails(lessonsArray[dayIndex][timeIndex], $event) : null"
            >
              <tr
                v-for="lesson in lessonsArray[mobile ? day + 1 : dayIndex][timeIndex]"
                :key="lesson.day + lesson.class + lesson.time + lesson.teacher"
                class="d-flex"
                :class="{ 'justify-space-between': mobile, 'justify-space-evenly': !mobile }"
              >
                <TimetableLesson :lesson="lesson" />
              </tr>
            </td>
          </template>
        </tr>
      </tbody>
    </v-table>
    <TimetableDetails v-model="lessonDetailsDialog" :lessons="lessonsDetails" />
  </div>
</template>
