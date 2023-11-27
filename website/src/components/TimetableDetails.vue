<script setup lang="ts">
import { storeToRefs } from 'pinia'
import type { MergedLesson } from '@/stores/timetable'

import { weekdays } from '@/composables/days'
import { lessonTimes } from '@/composables/times'
import { useUserStore } from '@/stores/user'

import { EntityType } from '@/stores/settings'

const { lessons } = defineProps<{ lessons: MergedLesson[] }>()

const { entityType } = storeToRefs(useUserStore())
</script>

<template>
  <v-card>
    <v-card-title class="text-uppercase">{{ lessons[0].time }}. ura</v-card-title>
    <v-card-subtitle class="text-capitalize">
      {{ weekdays[lessons[0].day - 1] }}, {{ lessonTimes[lessons[0].time][0] }} -
      {{ lessonTimes[lessons[0].time][1] }}
    </v-card-subtitle>
    <v-card-text class="px-4 pb-2 pt-2" v-for="lesson in lessons">
      <template v-if="lesson.substitution">
        <span>Predmet: {{ lesson.subject }} → {{ lesson.substitutionSubject }}</span
        ><br />
        <template v-if="entityType === EntityType.Class">
          <span>Profesor: {{ lesson.teacher }} → {{ lesson.substitutionTeacher }}</span
          ><br />
          <span>Učilnica: {{ lesson.classroom }} → {{ lesson.substitutionClassroom }}</span>
        </template>
        <template v-else-if="entityType === EntityType.Teacher">
          <span>Razred: {{ lesson.class }} </span><br />
          <span>Učilnica: {{ lesson.classroom }} → {{ lesson.substitutionClassroom }}</span>
        </template>
        <template v-else>
          <span>Razred: {{ lesson.class }} </span><br />
          <span>Profesor: {{ lesson.teacher }} → {{ lesson.substitutionTeacher }}</span>
        </template>
      </template>
    </v-card-text>
    <v-card-actions class="pt-0">
      <v-spacer></v-spacer>
      <v-btn color="green" @click="$emit('closeDialog')">Zapri</v-btn>
    </v-card-actions>
  </v-card>
</template>

<style>
.v-list-item__content {
  display: flex;
  justify-content: start;
}
</style>
