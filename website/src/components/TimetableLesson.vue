<script setup lang="ts">
import { storeToRefs } from 'pinia'

import TimetableLessonLink from '@/components/TimetableLessonLink.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'

const { lesson } = defineProps<{ lesson: MergedLesson }>()

const { entityType } = storeToRefs(useSessionStore())

const settingsStore = useSettingsStore()
const { showSubstitutions } = settingsStore

const subject =
  showSubstitutions && lesson.substitution ? lesson.substitutionSubject : lesson.subject

const links = {
  class: {
    entityTypeLink: EntityType.Class,
    substitution: lesson.substitution,
    originalEntity: lesson.class || '/',
    substitutionEntity: lesson.class || '/',
  },
  teacher: {
    entityTypeLink: EntityType.Teacher,
    substitution: lesson.substitution,
    originalEntity: lesson.teacher || '/',
    substitutionEntity: lesson.substitutionTeacher || '/',
  },
  classroom: {
    entityTypeLink: EntityType.Classroom,
    substitution: lesson.substitution,
    originalEntity: lesson.classroom || '/',
    substitutionEntity: lesson.substitutionClassroom || '/',
  },
  emptyClassrooms: {
    entityTypeLink: EntityType.EmptyClassrooms,
    substitution: lesson.substitution,
    originalEntity: lesson.classroom || '/',
    substitutionEntity: lesson.substitutionClassroom || '/',
  },
}
</script>

<template>
  <td>{{ subject }}</td>
  <template v-if="entityType === EntityType.Class">
    <TimetableLessonLink v-bind="links.teacher" />
    <TimetableLessonLink v-bind="links.classroom" />
  </template>
  <template v-else-if="entityType === EntityType.Teacher">
    <TimetableLessonLink v-bind="links.class" />
    <TimetableLessonLink v-bind="links.classroom" />
  </template>
  <template v-else-if="entityType === EntityType.Classroom">
    <TimetableLessonLink v-bind="links.class" />
    <TimetableLessonLink v-bind="links.teacher" />
  </template>
  <template v-else>
    <TimetableLessonLink v-bind="links.emptyClassrooms" />
    <div />
  </template>
</template>
