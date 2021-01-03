<!-- Component for displaying navigation between days in week -->

<template>
  <v-tabs v-model="currentDay" align-with-title center-active centered>
    <v-tabs-slider color="white" />
    <v-tab v-for="day in daysInWeek" :key="day">
      {{ day }}
    </v-tab>
  </v-tabs>
</template>

<style lang="scss">
// Hide blank space before first tab on mobile
.v-slide-group__prev {
  display: none !important;
}

// Change text color to white
.v-tab--active {
  color: #fff !important;
}
</style>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { StateModule } from '@/store/modules/state'
import { daysInWeek } from '@/utils/days'

@Component
export default class DayNavigation extends Vue {
  daysInWeek = daysInWeek

  get currentDay (): number {
    return StateModule.currentDay
  }

  set currentDay (currentDay: number) {
    StateModule.setCurrentDay(currentDay)
  }
}
</script>
