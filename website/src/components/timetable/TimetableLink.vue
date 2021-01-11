<!-- Display link to class/teacher/classroom if links are enabled -->

<template>
  <router-link v-if="type === 'class' && linksEnabled" :to="{ name: 'timetable', params: { type: 'classes', value: content } }" class="text-decoration-none">{{ content }}</router-link>
  <router-link v-else-if="type === 'teacher' && linksEnabled" :to="{ name: 'timetable', params: { type: 'teachers', value: content } }" class="text-decoration-none">{{ content }}</router-link>
  <router-link v-else-if="type === 'classroom' && linksEnabled" :to="{ name: 'timetable', params: { type: 'classrooms', value: content } }" class="text-decoration-none">{{ content }}</router-link>
  <span v-else>{{ content }}</span>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'

@Component
export default class TimetableLink extends Vue {
  @Prop() readonly content!: string
  @Prop() readonly type!: string

  get linksEnabled (): boolean {
    return SettingsModule.showLinksInTimetable
  }
}
</script>
