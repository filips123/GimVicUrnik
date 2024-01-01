<script setup lang="ts">
import { storeToRefs } from 'pinia'

import type { MergedLesson } from '@/stores/timetable'
import { useUserStore } from '@/stores/user'
import { useSettingsStore, EntityType } from '@/stores/settings'

import TimetableLink from '@/components/TimetableLink.vue'

const { lesson } = defineProps<{ lesson: MergedLesson }>()

const { entityType } = storeToRefs(useUserStore())

const settingsStore = useSettingsStore()
const { showSubstitutions } = settingsStore
</script>

<template>
  <td>
    {{ showSubstitutions && lesson.substitution ? lesson.substitutionSubject : lesson.subject }}
  </td>
  <template v-if="entityType === EntityType.Class">
    <TimetableLink
      :entityType="EntityType.Teacher"
      :substitution="lesson.substitution"
      :originalEntity="lesson.teacher"
      :substitutionEntity="lesson.substitutionTeacher"
    />
    <TimetableLink
      :entityType="EntityType.Classroom"
      :substitution="lesson.substitution"
      :originalEntity="lesson.classroom"
      :substitutionEntity="lesson.substitutionClassroom"
    />
  </template>
  <template v-else-if="entityType === EntityType.Teacher">
    <TimetableLink
      :entityType="EntityType.Class"
      :substitution="lesson.substitution"
      :originalEntity="lesson.class"
      :substitutionEntity="lesson.class"
    />
    <TimetableLink
      :entityType="EntityType.Classroom"
      :substitution="lesson.substitution"
      :originalEntity="lesson.classroom"
      :substitutionEntity="lesson.substitutionClassroom"
    />
  </template>
  <template v-else>
    <TimetableLink
      :entityType="EntityType.Class"
      :substitution="lesson.substitution"
      :originalEntity="lesson.class"
      :substitutionEntity="lesson.class"
    />
    <TimetableLink
      :entityType="EntityType.Teacher"
      :substitution="lesson.substitution"
      :originalEntity="lesson.teacher"
      :substitutionEntity="lesson.substitutionTeacher"
    />
  </template>
</template>
