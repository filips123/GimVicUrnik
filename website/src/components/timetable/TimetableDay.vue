<!-- Display timetable table for the specified day -->

<template>
  <v-sheet class="ma-3" elevation="4">
    <v-simple-table class="timetable-day">
      <template v-slot:default>
        <tbody>
          <tr v-for="lesson in lessons" :key="lesson.time" v-bind:class="{ highlight: lesson.substitution }">
            <td v-if="lesson.time === 0" class="timetable-time">PU</td>
            <td v-else class="timetable-time">{{ lesson.time }}.</td>

            <td v-for="data in lesson.data" :key="data.type">
                <span v-for="(value, index) in data.data" :key="index">
                  <span v-if="index !== 0" v-html="separator"></span>
                  <timetable-link :content="value" :type="data.type" />
                </span>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-sheet>
</template>

<style lang="scss">
// Wrap text in cells
.timetable-day > .v-data-table__wrapper > table > tbody {
  overflow-wrap: anywhere;
  text-align: center;
}

// Recover original font size
.timetable-day > .v-data-table__wrapper > table > tbody > tr > td {
  font-size: unset !important;
}

// Disable background change on hover
.timetable-day > .v-data-table__wrapper > table > tbody > tr:hover {
  background: transparent !important;
}

// Move time cell a bit more to the left
.timetable-time {
  max-width: 60px;
  min-width: 40px;
  padding-right: 0 !important;
}

// Set substitution highlights
.theme--light .highlight {
  background: #eee !important;
}

.theme--dark .highlight {
  background: #616161 !important;
}

</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import TimetableLink from '@/components/timetable/TimetableLink.vue'
import { EntityType, SelectedEntity, SettingsModule } from '@/store/modules/settings'
import { StateModule } from '@/store/modules/state'
import { DisplayedLesson, getLessonId, StorageModule } from '@/store/modules/storage'

@Component({
  components: { TimetableLink }
})
export default class TimetableDay extends Vue {
  @Prop() readonly currentDay!: number
  // There is also zero-width space so it can wrap in a better way
  separator = '/&#8203;'

  get currentEntity (): SelectedEntity | null {
    return StateModule.currentEntity
  }

  get lessons (): {
    time: number,
    substitution: boolean,
    data: {
      type: string,
      data: string[]
    }[]
  }[] {
    const dataSource = this.currentEntity?.type !== EntityType.EmptyClassrooms ? StorageModule.timetable : StorageModule.emptyClassrooms
    const substitutionsSource = this.currentEntity?.type === EntityType.Class ? StorageModule.substitutions : new Map()

    const displayedLessons: Map<number, DisplayedLesson> = new Map()
    for (const lesson of dataSource || []) {
      // Check if class/teacher/classroom is correct
      let isCorrectEntity = false
      if (this.currentEntity?.type === EntityType.Class) {
        isCorrectEntity = this.currentEntity.data.includes(lesson.class)
      } else if (this.currentEntity?.type === EntityType.Teacher) {
        isCorrectEntity = this.currentEntity.data.includes(lesson.teacher)
      } else if (this.currentEntity?.type === EntityType.Classroom) {
        isCorrectEntity = this.currentEntity.data.includes(lesson.classroom)
      } else if (this.currentEntity?.type === EntityType.EmptyClassrooms) isCorrectEntity = true

      if (lesson.day !== this.currentDay + 1 || !isCorrectEntity) continue

      // Convert data into structured format
      if (!displayedLessons.has(lesson.time)) {
        displayedLessons.set(lesson.time, {
          day: lesson.day,
          time: lesson.time,
          subjects: [],
          classes: [],
          teachers: [],
          classrooms: [],
          substitution: false
        })
      }

      // TODO: Add support for substitutions for teachers and classrooms

      // Add substitution if it exists
      // Currently only works for classes
      if (SettingsModule.showSubstitutions && substitutionsSource.has(getLessonId(lesson))) {
        const substitution = substitutionsSource.get(getLessonId(lesson))

        /* eslint-disable no-unused-expressions */
        displayedLessons.get(lesson.time)?.subjects.push(substitution.subject)
        displayedLessons.get(lesson.time)?.classes.push(substitution.class)
        displayedLessons.get(lesson.time)?.teachers.push(substitution.teacher)
        displayedLessons.get(lesson.time)?.classrooms.push(substitution.classroom)
        /* eslint-enable */

        const displayedLesson = displayedLessons.get(lesson.time)
        if (displayedLesson) displayedLesson.substitution = true

        continue
      }

      /* eslint-disable no-unused-expressions */
      displayedLessons.get(lesson.time)?.subjects.push(lesson.subject)
      displayedLessons.get(lesson.time)?.classes.push(lesson.class)
      displayedLessons.get(lesson.time)?.teachers.push(lesson.teacher)
      displayedLessons.get(lesson.time)?.classrooms.push(lesson.classroom)
      /* eslint-enable */
    }

    const data = []

    // Convert lessons of class into displayed format
    if (this.currentEntity?.type === EntityType.Class) {
      for (const displayedLesson of displayedLessons.values()) {
        data.push({
          time: displayedLesson.time,
          substitution: displayedLesson.substitution,
          data: [
            {
              type: 'subject',
              data: displayedLesson.subjects
            },
            {
              type: 'teacher',
              data: displayedLesson.teachers
            },
            {
              type: 'classroom',
              data: displayedLesson.classrooms
            }
          ]
        })
      }
    }

    // Convert lessons of teacher into displayed format
    if (this.currentEntity?.type === EntityType.Teacher) {
      for (const displayedLesson of displayedLessons.values()) {
        data.push({
          time: displayedLesson.time,
          substitution: displayedLesson.substitution,
          data: [
            {
              type: 'class',
              data: displayedLesson.classes
            },
            {
              type: 'subject',
              data: displayedLesson.subjects
            },
            {
              type: 'classroom',
              data: displayedLesson.classrooms
            }
          ]
        })
      }
    }

    // Convert lessons of classroom into displayed format
    if (this.currentEntity?.type === EntityType.Classroom) {
      for (const displayedLesson of displayedLessons.values()) {
        data.push({
          time: displayedLesson.time,
          substitution: displayedLesson.substitution,
          data: [
            {
              type: 'class',
              data: displayedLesson.classes
            },
            {
              type: 'subject',
              data: displayedLesson.subjects
            },
            {
              type: 'teacher',
              data: displayedLesson.teachers
            }
          ]
        })
      }
    }

    // Convert lessons of empty classroom into displayed format
    if (this.currentEntity?.type === EntityType.EmptyClassrooms) {
      for (const displayedLesson of displayedLessons.values()) {
        data.push({
          time: displayedLesson.time,
          substitution: false,
          data: [
            {
              type: 'classroom',
              data: displayedLesson.classrooms
            }
          ]
        })
      }
    }

    // Change separator if needed
    this.separator = this.currentEntity?.type !== EntityType.EmptyClassrooms ? '/&#8203;' : ' - '

    return data
  }
}
</script>
