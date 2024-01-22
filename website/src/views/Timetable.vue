<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
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

document.title = import.meta.env.VITE_TITLE + ' - Urnik'

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

let lessonsDetails = reactive([] as MergedLesson[])

function handleDetails(lessons: MergedLesson[], event: Event) {
  if (!enableShowingDetails || (event?.target as HTMLInputElement)?.classList.contains('text-blue'))
    return

  if (lessons.length) {
    lessonsDetails = lessons
    lessonDetailsDialog.value = true
  }
}

// Class bindings
function styleMobile(timeIndex: number) {
  return {
    'highlight-substitution':
      mobile.value &&
      showSubstitutions &&
      lessonsArray.value[day.value + 1][timeIndex]?.find((lesson) => lesson.substitution),
  }
}

function styleDesktop(dayIndex: number, timeIndex: number) {
  return {
    'highlight-substitution':
      !mobile.value &&
      showSubstitutions &&
      lessonsArray.value[dayIndex][timeIndex].find((lesson) => lesson.substitution),
    'highlight-day': !mobile.value && dayIndex - 1 === currentDay.value,
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
    class="h-auto"
  >
    <v-sheet elevation="2">
      <v-table>
        <thead>
          <tr v-if="!mobile">
            <th class="text-center" :colspan="showHoursInTimetable ? 2 : 1">Ura</th>
            <th
              v-for="(weekday, index) in localizedWeekdays"
              :key="index"
              :class="{ 'highlight-light': index === day }"
              class="text-center"
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
              <td class="text-center" :class="styleMobileCurrentTime(timeIndex)">
                {{ timeIndex === 0 ? 'Predura' : timeIndex + '.' }}
              </td>
              <template v-if="!mobile">
                <td class="text-center" v-if="showHoursInTimetable">
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
                  :key="lesson.day + lesson.class + lesson.time"
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

      <v-dialog v-model="lessonDetailsDialog" width="25rem">
        <TimetableDetails :lessons="lessonsDetails" @closeDialog="lessonDetailsDialog = false" />
      </v-dialog>
    </v-sheet>
  </div>
</template>

<style>
.current-time {
  position: relative;
  overflow: hidden;
}

.current-time:after {
  content: '';
  position: absolute;
  margin: -20px;
  width: 40px;
  height: 40px;
  transform: rotate(45deg);
  background-color: #009300;
  left: 0;
  top: 0;
}

.highlight-day {
  background: #f6f6f6;
}

.highlight-substitution {
  background: #d6d6d6;
}
</style>
