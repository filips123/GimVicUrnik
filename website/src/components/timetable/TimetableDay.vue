<!-- Display timetable table for the specified day -->

<template>
  <v-sheet class="ma-3" elevation="2">
    <v-simple-table class="timetable-day" v-bind:class="{ 'details-enabled': showDetails }">
      <template v-slot:default>
        <tbody>
          <tr v-for="lesson in lessons" :key="lesson.time"
            v-bind:class="{ highlight: lesson.substitution }"
            @click.stop="handleDetailsClick($event, currentDay, lesson.time, currentEntity)">
            <td v-if="lesson.time === 0" class="timetable-time">PU</td>
            <td v-else class="timetable-time">{{ lesson.time }}.</td>

            <td v-for="(detail, detailIndex) in lesson.details" :key="detail.type">
              <span v-if="detail.contents.length === 0 && detailIndex === Math.floor(lesson.details.length/2)">/</span>

              <span v-for="(value, valueIndex) in detail.contents" :key="valueIndex">
                <span v-if="valueIndex !== 0" v-html="separator"></span>
                <timetable-link :content="value" :type="detail.type" />
              </span>
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>

    <v-dialog v-model="lessonDetailsDialog" width="25rem">
      <lesson-details v-if="lessonDetailsDialog"
        @closeDialog="lessonDetailsDialog = false"
        v-bind:lesson-day="selectedLessonDay"
        v-bind:lesson-time="selectedLessonTime"
        v-bind:lesson-entity="selectedLessonEntity" />
    </v-dialog>
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

// Change background change on hover
.theme--light .timetable-day tr:not(.highlight):hover  {
  background: initial !important;
}

.theme--light .timetable-day.details-enabled tr:hover {
  background: #d9d9d9 !important;
}

.theme--dark .timetable-day tr:not(.highlight):hover  {
  background: initial !important;
}

.theme--dark .timetable-day.details-enabled tr:hover {
  background: #444 !important;
}

// Move time cell a bit more to the left
.timetable-day .timetable-time {
  max-width: 60px;
  min-width: 40px;
  padding-right: 0 !important;
}

// Set substitution highlights
.theme--light .highlight {
  background: #eee;
}

.theme--dark .highlight {
  background: #393939;
}

</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import LessonDetails from '@/components/timetable/LessonDetails.vue'
import TimetableLink from '@/components/timetable/TimetableLink.vue'
import { EntityType, SelectedEntity, SettingsModule } from '@/store/modules/settings'
import { StateModule } from '@/store/modules/state'
import { getTimetableData } from '@/utils/timetable'

@Component({
  components: { LessonDetails, TimetableLink }
})
export default class TimetableDay extends Vue {
  @Prop() readonly currentDay!: number
  // There is also zero-width space so it can wrap in a better way
  separator = '/&#8203;'

  lessonDetailsDialog = false
  selectedLessonDay?: number
  selectedLessonTime?: number
  selectedLessonEntity?: SelectedEntity

  get currentEntity (): SelectedEntity | null {
    return StateModule.currentEntity
  }

  get showDetails () :boolean {
    return SettingsModule.enableShowingDetails
  }

  get lessons (): {
    time: number,
    substitution: boolean,
    details: {
      type: string,
      contents: string[]
    }[]
  }[] {
    const displayedLessons = getTimetableData(this.currentEntity, [this.currentDay + 1]).get(this.currentDay + 1)
    const data = []

    if (!displayedLessons) return []

    // Convert lessons of class into displayed format
    if (this.currentEntity?.type === EntityType.Class) {
      for (const displayedLesson of displayedLessons.values()) {
        data.push({
          time: displayedLesson.time,
          substitution: displayedLesson.substitution,
          details: [
            {
              type: 'subject',
              contents: displayedLesson.subjects.filter(x => x)
            },
            {
              type: 'teacher',
              contents: displayedLesson.teachers
            },
            {
              type: 'classroom',
              contents: displayedLesson.classrooms.filter(x => x)
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
          details: [
            {
              type: 'class',
              contents: displayedLesson.classes
            },
            {
              type: 'subject',
              contents: displayedLesson.subjects.filter(x => x)
            },
            {
              type: 'classroom',
              contents: displayedLesson.classrooms.filter(x => x)
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
          details: [
            {
              type: 'class',
              contents: displayedLesson.classes
            },
            {
              type: 'subject',
              contents: displayedLesson.subjects
            },
            {
              type: 'teacher',
              contents: displayedLesson.teachers
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
          substitution: displayedLesson.substitution,
          details: [
            {
              type: 'classroom',
              contents: displayedLesson.classrooms.filter(x => x)
            }
          ]
        })
      }
    }

    // Change separator if needed
    this.separator = this.currentEntity?.type !== EntityType.EmptyClassrooms ? '/&#8203;' : ' - '

    return data.sort((a, b) => a.time - b.time)
  }

  handleDetailsClick (
    event: InputEvent,
    day: number,
    time: number,
    entity: SelectedEntity
  ): void {
    if (!this.showDetails || this.currentEntity?.type === EntityType.EmptyClassrooms) return
    if ((event.target as HTMLElement)?.tagName === 'A') return

    this.selectedLessonDay = day
    this.selectedLessonTime = time
    this.selectedLessonEntity = entity
    this.lessonDetailsDialog = true
  }
}
</script>
