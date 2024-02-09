<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import type { MergedLesson } from '@/stores/timetable'

import { localizedWeekdays } from '@/composables/localization'
import { lessonTimes } from '@/composables/times'
import { useUserStore } from '@/stores/user'

import { EntityType } from '@/stores/settings'

const props = defineProps<{
  modelValue: boolean
  lessons: MergedLesson[]
}>()

const emit = defineEmits(['update:modelValue'])

const detailsDialog = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { entityType } = storeToRefs(useUserStore())

const subtitle = computed(
  () =>
    localizedWeekdays[props.lessons[0].day - 1] +
    ', ' +
    lessonTimes[props.lessons[0].time][0] +
    ' - ' +
    lessonTimes[props.lessons[0].time][1],
)

const substitutionLessons = computed(() => {
  return props.lessons.filter((lesson) => lesson.substitution === true)
})
</script>

<template>
  <v-dialog v-model="detailsDialog">
    <v-card :title="lessons[0].time + '. URA'" :subtitle="subtitle">
      <v-card-text v-if="substitutionLessons.length">
        <div
          v-for="(lesson, index) in substitutionLessons"
          :class="{ 'mb-3': index !== substitutionLessons.length - 1 }"
        >
          <span>Predmet: {{ lesson.subject }} → {{ lesson.substitutionSubject }}</span> <br />
          <template v-if="entityType === EntityType.Class">
            <span>Profesor: {{ lesson.teacher }} → {{ lesson.substitutionTeacher }}</span> <br />
            <span>Učilnica: {{ lesson.classroom }} → {{ lesson.substitutionClassroom }}</span>
          </template>
          <template v-else-if="entityType === EntityType.Teacher">
            <span>Razred: {{ lesson.class }} </span><br />
            <span>Učilnica: {{ lesson.classroom }} → {{ lesson.substitutionClassroom }}</span>
          </template>
          <template v-else>
            <span>Razred: {{ lesson.class }}</span> <br />
            <span>Profesor: {{ lesson.teacher }} → {{ lesson.substitutionTeacher }}</span>
          </template>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="detailsDialog = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
