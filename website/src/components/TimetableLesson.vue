<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableLessonLink from '@/components/TimetableLessonLink.vue'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'

const props = defineProps<{ lesson: MergedLesson }>()

const { currentEntityType, currentEntityList } = storeToRefs(useSessionStore())
const { showSubstitutions } = storeToRefs(useSettingsStore())

const subjectName = computed(() =>
  showSubstitutions.value && props.lesson.isSubstitution
    ? props.lesson.substitutionSubject
    : props.lesson.subject,
)

const classLink = computed(() => ({
  linkType: 'classes',
  linkValue: props.lesson.class,
}))

const teacherLink = computed(() => ({
  linkType: 'teachers',
  linkValue:
    showSubstitutions.value && props.lesson.isSubstitution
      ? props.lesson.substitutionTeacher
      : props.lesson.teacher,
}))

const classroomLink = computed(() => ({
  linkType: 'classrooms',
  linkValue:
    showSubstitutions.value && props.lesson.isSubstitution
      ? props.lesson.substitutionClassroom
      : props.lesson.classroom,
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
  <template v-if="!isEmpty">
    <td class="w-33">{{ subjectName }}</td>
    <td v-if="currentEntityType !== EntityType.Class" class="w-33">
      <TimetableLessonLink v-bind="classLink" />
    </td>
    <td v-if="currentEntityType !== EntityType.Teacher" class="w-33">
      <TimetableLessonLink v-bind="teacherLink" />
    </td>
    <td v-if="currentEntityType !== EntityType.Classroom" class="w-33">
      <TimetableLessonLink v-bind="classroomLink" />
    </td>
  </template>
  <td v-else colspan="3">/</td>
</template>
