<!-- A dialog popup that displays more details about lesson -->

<template>
      <v-card>
        <v-card-title class="text-uppercase">{{ lessonName }}</v-card-title>
        <v-card-subtitle class="pb-1">{{ this.lessonDayStr }}, {{ this.lessonTimeStr }}</v-card-subtitle>

        <v-card-text class="pb-0">
          <div v-for="(substitution, index) in lessonContents" :key="index">
            <v-list dense class="lesson-details pb-3">
              <v-list-item class="px-0" v-if="lessonEntity.type !== EntityType.Class">
                <v-list-item-title>Razred</v-list-item-title>
                <v-list-item-subtitle>{{ substitution.class }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0">
                <v-list-item-title>Predmet</v-list-item-title>
                <v-list-item-subtitle>{{ substitution['original-subject'] }} → {{ substitution.subject }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0" v-if="lessonEntity.type !== EntityType.Teacher">
                <v-list-item-title>Profesor</v-list-item-title>
                <v-list-item-subtitle>{{ substitution['original-teacher'] }} → {{ substitution.teacher }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0" v-if="lessonEntity.type !== EntityType.Classroom">
                <v-list-item-title>Učilnica</v-list-item-title>
                <v-list-item-subtitle>{{ substitution['original-classroom']}} → {{ substitution.classroom }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item class="px-0" v-if="substitution.notes">
                <v-list-item-title style="">Opombe</v-list-item-title>
                <v-list-item-subtitle>{{ substitution.notes }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </div>
        </v-card-text>

        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn color="green" text v-on:click=closeDialog>Zapri</v-btn>
        </v-card-actions>
      </v-card>
</template>

<style lang="scss">
.lesson-details .v-list-item {
  min-height: 33px;
}

.lesson-details .v-list-item__title {
  max-width: 5rem;
}

.lesson-details .v-list-item__subtitle {
  white-space: break-spaces;
}

</style>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, SelectedEntity } from '@/store/modules/settings'
import { Lesson, StorageModule, Substitution } from '@/store/modules/storage'
import { daysInWeek } from '@/utils/days'
import { hourTimes } from '@/utils/hours'

interface DisplayedSubstitution extends Substitution {
  'original-subject': string;
}

@Component
export default class LessonDetails extends Vue {
  @Prop() readonly lessonDay!: number
  @Prop() readonly lessonTime!: number
  @Prop() readonly lessonEntity!: SelectedEntity

  EntityType = EntityType

  get lessonName (): string {
    return this.lessonTime ? `${this.lessonTime}. ura` : 'Predura'
  }

  get lessonDayStr (): string {
    return daysInWeek[this.lessonDay]
  }

  get lessonTimeStr (): string {
    return hourTimes[this.lessonTime]
  }

  get lessonContents (): DisplayedSubstitution[] {
    const substitutions: DisplayedSubstitution[] = []

    for (const substitution of StorageModule._substitutions?.[this.lessonDay] || []) {
      if (substitution.day !== this.lessonDay + 1 || substitution.time !== this.lessonTime) continue

      const entityType = this.lessonEntity.type
      const entityData = this.lessonEntity.data

      if (entityType === EntityType.Class && !entityData.includes(substitution.class)) continue
      if (entityType === EntityType.Teacher && !(entityData.includes(substitution.teacher) || entityData.includes(substitution['original-teacher']))) continue
      if (entityType === EntityType.Classroom && !(entityData.includes(substitution.classroom) || entityData.includes(substitution['original-classroom']))) continue

      substitutions.push({
        ...substitution,
        subject: substitution.subject || '/',
        teacher: substitution.teacher || '/',
        classroom: substitution.classroom || '/',
        'original-subject': StorageModule.timetable?.find(this.checkLesson)?.subject || '/',
        'original-teacher': substitution['original-teacher'] || '/',
        'original-classroom': substitution['original-classroom'] || '/'
      })
    }

    return substitutions
  }

  checkLesson (lesson: Lesson): boolean {
    if (lesson.day !== this.lessonDay + 1 || lesson.time !== this.lessonTime) return false

    const entityType = this.lessonEntity.type
    const entityData = this.lessonEntity.data

    if (entityType === EntityType.Class && !entityData.includes(lesson.class)) return false
    if (entityType === EntityType.Teacher && !entityData.includes(lesson.teacher)) return false
    if (entityType === EntityType.Classroom && !entityData.includes(lesson.classroom)) return false

    return true
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
