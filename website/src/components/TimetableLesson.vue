<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableLessonLink from '@/components/TimetableLessonLink.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'

const { lesson } = defineProps<{ lesson: MergedLesson }>()

const { currentEntityType, currentEntityList } = storeToRefs(useSessionStore())
const { showSubstitutions } = storeToRefs(useSettingsStore())

const subjectName = computed(() =>
  showSubstitutions.value && lesson.isSubstitution ? lesson.substitutionSubject : lesson.subject,
)

const classLink = computed(() => ({
  linkType: 'classes',
  linkValue: lesson.class,
}))

const teacherLink = computed(() => ({
  linkType: 'teachers',
  linkValue:
    showSubstitutions.value && lesson.isSubstitution //
      ? lesson.substitutionTeacher
      : lesson.teacher,
}))

const classroomLink = computed(() => ({
  linkType: 'classrooms',
  linkValue:
    showSubstitutions.value && lesson.isSubstitution //
      ? lesson.substitutionClassroom
      : lesson.classroom,
}))

const isEmpty = computed(() => {
  // A lesson for teacher is also empty if the teacher has been changed
  if (
    currentEntityType.value === EntityType.Teacher &&
    !currentEntityList.value.includes(teacherLink.value.linkValue!)
  ) {
    return true
  }

  // A lesson for classroom is also empty if the classroom has been changed
  if (
    currentEntityType.value === EntityType.Classroom &&
    !currentEntityList.value.includes(classroomLink.value.linkValue!)
  ) {
    return true
  }

  // In any case, a lesson is empty if it has no teacher and classroom
  // Note that some lessons (VAJE) do not have a subject but are not empty
  return !teacherLink.value.linkValue && !classroomLink.value.linkValue
})
</script>

<template>
  <template v-if="currentEntityType !== EntityType.EmptyClassrooms">
    <!-- prettier-ignore -->
    <template v-if="!isEmpty">
      <td>{{ subjectName }}</td>
      <td v-if="currentEntityType !== EntityType.Class"><TimetableLessonLink v-bind="classLink" /></td>
      <td v-if="currentEntityType !== EntityType.Teacher"><TimetableLessonLink v-bind="teacherLink" /></td>
      <td v-if="currentEntityType !== EntityType.Classroom"><TimetableLessonLink v-bind="classroomLink" /></td>
    </template>
    <td v-else>/</td>
  </template>

  <template v-else>
    <TimetableLessonLink v-bind="classroomLink" />
  </template>
</template>
