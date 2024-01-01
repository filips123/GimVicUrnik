<script setup lang="ts">
import { storeToRefs } from 'pinia'
import type { MergedLesson } from '@/stores/timetable'

import { localizedWeekdays } from '@/composables/localization'
import { lessonTimes } from '@/composables/times'
import { useUserStore } from '@/stores/user'

import { EntityType } from '@/stores/settings'

const props = defineProps<{ lessons: MergedLesson[] }>()

const { entityType } = storeToRefs(useUserStore())

const subtitle =
  localizedWeekdays[props.lessons[0].day - 1] +
  ', ' +
  lessonTimes[props.lessons[0].time][0] +
  ' - ' +
  lessonTimes[props.lessons[0].time][1]
</script>

<template>
  <v-card :title="lessons[0].time + '. URA'" :subtitle="subtitle">
    <v-card-text>
      <template v-for="lesson in lessons">
        <template v-if="lesson.substitution">
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
          <br /><br />
        </template>
      </template>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="green" @click="$emit('closeDialog')" text="Zapri" />
    </v-card-actions>
  </v-card>
</template>
