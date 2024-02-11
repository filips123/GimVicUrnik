<script setup lang="ts">
import { EntityType } from '@/stores/settings'
import type { MergedLesson } from '@/stores/timetable'
import { useUserStore } from '@/stores/user'
import { localizedWeekdays } from '@/utils/localization'
import { lessonTimes } from '@/utils/times'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

const dialog = defineModel<boolean>()
const props = defineProps<{ lessons: MergedLesson[] }>()

const { entityType } = storeToRefs(useUserStore())

const title = computed(() => (props.lessons[0].time !== 0 ? `${props.lessons[0].time}. ura` : 'pu'))

const day = computed(() => localizedWeekdays[props.lessons[0].day - 1])
const lessonTime = computed(() => lessonTimes[props.lessons[0].time].join(' - '))
const subtitle = computed(() => `${day.value}, ${lessonTime.value}`)

const substitutionLessons = computed(() =>
  props.lessons.filter((lesson) => lesson.substitution === true),
)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card :title :subtitle>
      <template v-if="substitutionLessons.length" #text>
        <div
          v-for="(lesson, index) in substitutionLessons"
          :key="index"
          :class="{ 'mb-3': index !== substitutionLessons.length - 1 }"
        >
          <template v-if="entityType === EntityType.Class">
            <div class="text-primary-variant">{{ lesson.class }}</div>
            <div
              v-if="lesson.teacher !== lesson.substitutionTeacher"
              v-text="'Profesor: ' + lesson.teacher + ' → ' + lesson.substitutionTeacher"
            ></div>
            <div
              v-if="lesson.classroom !== lesson.substitutionClassroom"
              v-text="'Razred: ' + lesson.classroom + ' → ' + lesson.substitutionClassroom"
            ></div>
          </template>
          <template v-else-if="entityType === EntityType.Teacher">
            <div class="text-primary-variant">{{ lesson.teacher }}</div>
            <div>Razred: {{ lesson.class }}</div>
            <div
              v-if="lesson.classroom !== lesson.substitutionClassroom"
              v-text="'Razred: ' + lesson.classroom + ' → ' + lesson.substitutionClassroom"
            ></div>
          </template>
          <template v-else>
            <div class="text-primary-variant">{{ lesson.classroom }}</div>
            <div>Razred: {{ lesson.class }}</div>
            <div
              v-if="lesson.teacher !== lesson.substitutionTeacher"
              v-text="'Profesor: ' + lesson.teacher + ' → ' + lesson.substitutionTeacher"
            ></div>
          </template>
          <div
            v-if="lesson.subject !== lesson.substitutionSubject"
            v-text="'Predmet: ' + lesson.subject + ' → ' + lesson.substitutionSubject"
          ></div>
        </div>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
