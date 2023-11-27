<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

import { type MergedLesson, useTimetableStore } from '@/stores/timetable'
import { useSettingsStore, EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

import { lessonTimes, getCurrentTime } from '@/composables/times'
import { weekdays, getCurrentDay } from '@/composables/days'

import TimetableLink from '@/components/TimetableLink.vue'
import TimetableDetails from '@/components/TimetableDetails.vue'

document.title = import.meta.env.VITE_TITLE + ' - Urnik'

const { mobile } = useDisplay()

const userStore = useUserStore()
const timetableStore = useTimetableStore()
const settingsStore = useSettingsStore()

timetableStore.updateTimetable()
timetableStore.updateSubstitutions()
timetableStore.updateEmptyClassrooms()

userStore.resetData()

const lessonDetailsDialog = ref(false)

const { day, entityType } = storeToRefs(useUserStore())
const { showHoursInTimetable, showSubstitutions } = settingsStore

const maxLessonTime = computed(() => {
  const lessons = !mobile.value
    ? timetableStore.lessons
    : timetableStore.lessons.filter((lesson) => lesson.day == day.value + 1)
  return (
    lessons.reduce(
      (maxTime, lesson) => (lesson?.time > maxTime ? lesson?.time : maxTime),
      lessons[0]?.time
    )
  )
})

const minLessonTime = computed(() => {
  const lessons = !mobile.value
    ? timetableStore.lessons
    : timetableStore.lessons.filter((lesson) => lesson.day == day.value + 1)
  return (
    lessons.reduce(
      (minTime, lesson) => (lesson.time < minTime ? lesson.time : minTime),
      lessons[0]?.time
    )
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

let detailsLessons = reactive([] as MergedLesson[])

function handleDetails(lessons: MergedLesson[], event: Event) {
  if ((event?.target as HTMLInputElement)?.classList.contains('text-blue')) {
    return
  }

  if (lessons.length) {
    detailsLessons = lessons
    lessonDetailsDialog.value = true
  }
}
</script>
<template>
  <v-sheet elevation="2">
    <v-table class="timetable-day">
      <thead>
        <tr v-if="!mobile">
          <th class="timetable-time text-center" :colspan="showHoursInTimetable ? 2 : 1">Ura</th>
          <th
            v-for="(weekday, index) in weekdays"
            class="text-center"
            :class="{ 'highlight-light': index === day }"
          >
            {{ weekday }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="timeIndex in maxLessonTime"
          :class="{
            'highlight-substitution':
              mobile &&
              showSubstitutions &&
              lessonsArray[day + 1][timeIndex]?.find((lesson) => lesson.substitution)
          }"
          @click="mobile ? handleDetails(lessonsArray[day + 1][timeIndex], $event) : null"
        >
          <template v-if="timeIndex >= minLessonTime">
            <td
              class="timetable-time"
              :class="{
                'current-time': mobile && day === getCurrentDay() && timeIndex === getCurrentTime()
              }"
            >
              {{ timeIndex === 0 ? 'Predura' : timeIndex + '.' }}
            </td>
            <template v-if="!mobile">
              <td v-if="showHoursInTimetable" class="timetable-hour">
                {{ lessonTimes[timeIndex][0] }} - {{ lessonTimes[timeIndex][1] }}
              </td>
            </template>
            <td
              v-for="dayIndex in mobile ? 1 : 5"
              :class="{
                'highlight-substitution':
                  !mobile &&
                  lessonsArray[dayIndex][timeIndex].find((lesson) => lesson.substitution),
                'highlight-day': !mobile && dayIndex - 1 === getCurrentDay(),
                'current-time':
                  !mobile && dayIndex - 1 === getCurrentDay() && timeIndex === getCurrentTime()
              }"
              @click="!mobile ? handleDetails(lessonsArray[dayIndex][timeIndex], $event) : null"
            >
              <tr
                class="d-flex"
                :class="{ 'justify-space-between': mobile, 'justify-space-evenly': !mobile }"
                v-for="lesson in lessonsArray[mobile ? day + 1 : dayIndex][timeIndex]"
              >
                <td>
                  {{
                    showSubstitutions && lesson.substitution
                      ? lesson.substitutionSubject
                      : lesson.subject
                  }}
                </td>
                <template v-if="entityType === EntityType.Class">
                  <timetable-link
                    :entityType="EntityType.Teacher"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.teacher"
                    :substitutionEntity="lesson.substitutionTeacher"
                  />
                  <timetable-link
                    :entityType="EntityType.Classroom"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.classroom"
                    :substitutionEntity="lesson.substitutionClassroom"
                  />
                </template>
                <template v-else-if="entityType === EntityType.Teacher">
                  <timetable-link
                    :entityType="EntityType.Class"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.class"
                    :substitutionEntity="lesson.class"
                  />
                  <timetable-link
                    :entityType="EntityType.Classroom"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.classroom"
                    :substitutionEntity="lesson.substitutionClassroom"
                  />
                </template>
                <template v-else>
                  <timetable-link
                    :entityType="EntityType.Class"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.class"
                    :substitutionEntity="lesson.class"
                  />
                  <timetable-link
                    :entityType="EntityType.Teacher"
                    :substitution="lesson.substitution"
                    :originalEntity="lesson.teacher"
                    :substitutionEntity="lesson.substitutionTeacher"
                  />
                </template>
              </tr>
            </td>
          </template>
        </tr>
      </tbody>
    </v-table>

    <v-dialog v-model="lessonDetailsDialog" width="25rem">
      <timetable-details :lessons="detailsLessons" @closeDialog="lessonDetailsDialog = false" />
    </v-dialog>
  </v-sheet>
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
  bottom: 0;
}

.highlight-day {
  background: #f6f6f6;
}

.highlight-substitution {
  background: #d6d6d6;
}
</style>
