<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import TimetableLessonLink from '@/components/TimetableLessonLink.vue'
import { EntityType, useSettingsStore } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'
import { sortEntities } from '@/utils/entities'

const props = defineProps<{ lessons: MergedLesson[] }>()

const { showSubstitutions } = storeToRefs(useSettingsStore())

const emptyClassrooms = computed(() => {
  if (!showSubstitutions.value) {
    return sortEntities(
      EntityType.EmptyClassrooms,
      props.lessons.map(lesson => lesson.classroom!),
    )
  }

  const occupiedClassrooms = new Set<string>()
  const emptyClassrooms = new Set<string>()

  for (const lesson of props.lessons) {
    if (lesson.substitutionClassroom) occupiedClassrooms.add(lesson.substitutionClassroom)
    if (lesson.classroom) emptyClassrooms.add(lesson.classroom)
  }

  // Final empty classrooms are those in empty classrooms but not in occupied classrooms
  for (const classroom of occupiedClassrooms) {
    emptyClassrooms.delete(classroom)
  }

  return sortEntities(EntityType.EmptyClassrooms, [...emptyClassrooms])
})
</script>

<template>
  <div class="px-2">
    <template v-for="(classroom, index) in emptyClassrooms" :key="`${classroom}-${index}`">
      <template v-if="index > 0">, </template>
      <TimetableLessonLink link-type="classrooms" :link-value="classroom" />
    </template>
  </div>
</template>
