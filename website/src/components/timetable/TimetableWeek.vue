<!-- Display timetable table for the current week -->

<template>
  <v-sheet class="ma-6" elevation="4">
    <v-simple-table class="timetable-week">
      <template v-slot:default>
        <thead>
          <tr>
            <th class="timetable-time">Ura</th>
            <th v-for="(name, index) in daysInWeek"
              :key="index"
              v-bind:class="{ 'highlight-light': index === currentDay }">{{ name }}
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="lesson in lessons" :key="lesson.time">
            <template v-if="lesson.days">
              <td v-if="lesson.time === 0" class="timetable-time">PU</td>
              <td v-else class="timetable-time">{{ lesson.time }}.</td>
            </template>
            <td v-for="(data, day) in lesson.days"
              :key="day"
              v-bind:class="{ 'highlight-light': day === currentDay, highlight: data.substitution }">
              <span v-if="data.substitution && !data.details">/</span>
              <span v-for="(detail, detailIndex) in data.details" :key="detail.type">
                <span v-if="detailIndex !== 0" v-html="detailSeparator"></span>
                  <span v-for="(value, valueIndex) in detail.contents" :key="valueIndex">
                    <span v-if="valueIndex !== 0" v-html="contentSeparator"></span>
                    <timetable-link :content="value" :type="detail.type" />
                  </span>
              </span>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-sheet>
</template>

<style lang="scss">
// Wrap text in cells and set height
.timetable-week > .v-data-table__wrapper > table > thead > tr > th,
.timetable-week > .v-data-table__wrapper > table > tbody > tr > td {
  overflow-wrap: anywhere;
  padding: 20px 16px !important;
  text-align: center !important;
}

// Recover original font size
.timetable-week > .v-data-table__wrapper > table > thead > tr > th,
.timetable-week > .v-data-table__wrapper > table > tbody > tr > td {
  font-size: unset !important;
}

// Disable background change on hover
.timetable-week > .v-data-table__wrapper > table > tbody > tr:hover {
  background: transparent !important;
}

// Move time cell a bit more to the left
.timetable-week .timetable-time {
  max-width: 60px;
  min-width: 40px;
  padding-left: 8px !important;
  padding-right: 0 !important;
}

// Set substitution highlights
.theme--light .highlight {
  background: #eee !important;
}

.theme--dark .highlight {
  background: #393939 !important;
}

// Set current day highlight
.theme--light .highlight-light {
  background: #f8f8f8;
}

.theme--dark .highlight-light {
  background: #282828;
}
</style>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { EntityType, SelectedEntity } from '@/store/modules/settings'
import { StateModule } from '@/store/modules/state'
import { daysInWeek, getCurrentDay } from '@/utils/days'
import { getTimetableData } from '@/utils/timetable'

import TimetableLink from './TimetableLink.vue'

@Component({
  components: { TimetableLink }
})
export default class TimetableWeek extends Vue {
  daysInWeek = daysInWeek
  currentDay = getCurrentDay()

  detailSeparator = ' - '
  contentSeparator = '/&#8203;'

  get currentEntity (): SelectedEntity | null {
    return StateModule.currentEntity
  }

  get lessons (): {
    time: number,
    days: {
      substitution: boolean,
      details: {
        type: string,
        contents: string[]
      }[] | undefined
    }[]
  }[] {
    const displayedLessons = getTimetableData(this.currentEntity, [1, 2, 3, 4, 5])

    // Get first and last lesson time in week
    const dayLengths = Array.from(displayedLessons, day => Array.from(day[1], time => time[1].time)).flat()
    const minTime = Math.min(...dayLengths)
    const maxTime = Math.max(...dayLengths)

    const data = []

    // Convert lessons of class into displayed format
    for (let time = minTime; time <= maxTime; time++) {
      const timeData: {
        time: number,
        days: {
          substitution: boolean,
          details: {
            type: string,
            contents: string[]
          }[] | undefined
        }[]
      } = {
        time: time,
        days: []
      }

      for (let day = 1; day <= 5; day++) {
        const lesson = displayedLessons.get(day)?.get(time)

        if (!lesson) {
          timeData.days.push({ substitution: false, details: undefined })
          continue
        }

        if (lesson.subjects.length === 0) {
          timeData.days.push({ substitution: true, details: undefined })
          continue
        }

        // Convert lessons of class into displayed format
        if (this.currentEntity?.type === EntityType.Class) {
          timeData.days.push({
            substitution: lesson.substitution,
            details: [
              {
                type: 'subject',
                contents: lesson.subjects
              },
              {
                type: 'teacher',
                contents: lesson.teachers
              },
              {
                type: 'classroom',
                contents: lesson.classrooms
              }
            ]
          })
        }

        // Convert lessons of teacher into displayed format
        if (this.currentEntity?.type === EntityType.Teacher) {
          timeData.days.push({
            substitution: lesson.substitution,
            details: [
              {
                type: 'class',
                contents: lesson.classes
              },
              {
                type: 'subject',
                contents: lesson.subjects
              },
              {
                type: 'classroom',
                contents: lesson.classrooms
              }
            ]
          })
        }

        // Convert lessons of classroom into displayed format
        if (this.currentEntity?.type === EntityType.Classroom) {
          timeData.days.push({
            substitution: lesson.substitution,
            details: [
              {
                type: 'class',
                contents: lesson.classes
              },
              {
                type: 'subject',
                contents: lesson.subjects
              },
              {
                type: 'teacher',
                contents: lesson.teachers
              }
            ]
          })
        }

        // Convert lessons of empty classroom into displayed format
        if (this.currentEntity?.type === EntityType.EmptyClassrooms) {
          timeData.days.push({
            substitution: false,
            details: [
              {
                type: 'classroom',
                contents: lesson.classrooms
              }
            ]
          })
        }
      }

      data.push(timeData)
    }

    // Change separator if needed
    this.contentSeparator = this.currentEntity?.type !== EntityType.EmptyClassrooms ? '/&#8203;' : ' - '

    return data
  }
}
</script>
