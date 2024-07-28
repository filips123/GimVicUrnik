<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableLessonLink from '@/components/TimetableLessonLink.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'

const { lesson } = defineProps<{ lesson: MergedLesson }>()

const { currentEntityType } = storeToRefs(useSessionStore())
const { showSubstitutions } = storeToRefs(useSettingsStore())

const subjectName = computed(() =>
  showSubstitutions.value && lesson.isSubstitution ? lesson.substitutionSubject : lesson.subject,
)

const classLink = computed(() => ({
  linkType: 'classes',
  isSubstitution: lesson.isSubstitution,
  originalEntity: lesson.class || '/',
  substitutionEntity: lesson.class || '/',
}))

const teacherLink = computed(() => ({
  linkType: 'teachers',
  isSubstitution: lesson.isSubstitution,
  originalEntity: lesson.teacher || '/',
  substitutionEntity: lesson.substitutionTeacher || '/',
}))

const classroomLink = computed(() => ({
  linkType: 'classrooms',
  isSubstitution: lesson.isSubstitution,
  originalEntity: lesson.classroom || '/',
  substitutionEntity: lesson.substitutionClassroom || '/',
}))
</script>

<template>
  <template v-if="currentEntityType !== EntityType.EmptyClassrooms">
    <td>{{ subjectName || '/' }}</td>
    <TimetableLessonLink v-if="currentEntityType !== EntityType.Class" v-bind="classLink" />
    <TimetableLessonLink v-if="currentEntityType !== EntityType.Teacher" v-bind="teacherLink" />
    <TimetableLessonLink v-if="currentEntityType !== EntityType.Classroom" v-bind="classroomLink" />
  </template>

  <template v-else>
    <TimetableLessonLink v-bind="classroomLink" />
  </template>
</template>
