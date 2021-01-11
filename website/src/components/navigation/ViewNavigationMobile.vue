<!-- Component for displaying navigation between timetable/menus/documents views on mobile -->

<template>
  <v-bottom-navigation fixed grow>
    <v-btn :to="{ name: 'timetable' }">
      <span>Urnik</span>
      <v-icon>{{ mdiTimetable }}</v-icon>
    </v-btn>

    <v-btn :to="{ name: 'menus' }">
      <span>Jedilnik</span>
      <v-icon>{{ mdiFood }}</v-icon>
    </v-btn>

    <v-btn :to="{ name: 'documents' }">
      <span>Okrožnice</span>
      <v-icon>{{ mdiNewspaper }}</v-icon>
    </v-btn>
  </v-bottom-navigation>
</template>

<script lang="ts">
import { mdiFood, mdiNewspaper, mdiTimetable } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class ViewNavigationMobile extends Vue {
  mdiTimetable = mdiTimetable
  mdiFood = mdiFood
  mdiNewspaper = mdiNewspaper
}
</script>
