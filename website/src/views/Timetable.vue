<template>
  <v-row v-if="isReady && $root.$children[0].isMobile" class="timetable" justify="center">
    <v-tabs-items ref="tabs" v-model="currentDay" :touch="tabsItemsTouch">
      <v-tab-item v-for="(dayName, dayIndex) in daysInWeek" :key="dayIndex">
        <timetable-day :current-day="dayIndex" />
      </v-tab-item>
    </v-tabs-items>
  </v-row>

  <v-row v-else-if="isReady && !$root.$children[0].isMobile" class="timetable" justify="center">
    <timetable-week />
  </v-row>
  <loading v-else />
</template>

<style lang="scss">
// Fix background on dark theme and resize mobile timetable
.timetable > .v-tabs-items {
  background-color: unset !important;
  width: 100%;
}

// Set max desktop timetable width
.timetable > .v-sheet {
  width: min(110rem, 100%);
}

// Fix table height and width
.v-window__container {
  height: inherit !important;
  width: inherit !important;
}
</style>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import { Route } from 'vue-router'
import { TouchHandlers } from 'vuetify'

import Loading from '@/components/base/Loading.vue'
import { EntityType, SettingsModule } from '@/store/modules/settings'
import { StateModule } from '@/store/modules/state'
import { StorageModule } from '@/store/modules/storage'
import { daysInWeek } from '@/utils/days'

@Component({
  components: {
    TimetableDay: () => import(/* webpackChunkName: "mobile" */ '@/components/timetable/TimetableDay.vue'),
    TimetableWeek: () => import(/* webpackChunkName: "desktop" */ '@/components/timetable/TimetableWeek.vue'),
    Loading
  }
})
export default class Timetable extends Vue {
  daysInWeek = daysInWeek
  isReady = false

  // Custom touch function which does not stop propagation
  // This is needed for pull to refresh to work
  tabsItemsTouch: TouchHandlers = {
    left: () => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      this.$vuetify.rtl ? this.$refs.tabs.prev() : this.$refs.tabs.next()
    },
    right: () => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      this.$vuetify.rtl ? this.$refs.tabs.next() : this.$refs.tabs.prev()
    },
    end: () => undefined,
    start: () => undefined
  }

  get currentDay (): number {
    return StateModule.currentDay
  }

  set currentDay (currentDay: number) {
    StateModule.setCurrentDay(currentDay)
  }

  created (): void {
    this.$emit('setDayMenuDisplay', true)
    this.update()
  }

  @Watch('$route')
  onRouteChanged (newRoute: Route, oldRoute: Route): void {
    if (!newRoute || !oldRoute) return
    if (newRoute.fullPath === oldRoute.fullPath) return

    this.update()
  }

  async update (): Promise<void> {
    // Try to get entity based on route
    if (this.$route.params.type && this.$route.params.value) {
      // Update lists if needed
      if (!this.$route.params.skipListUpdate) await StorageModule.updateLists()

      // User is already on another page
      if (!this.$route.params.type || !this.$route.params.value) return

      const type = this.$route.params.type
      const data = this.$route.params.value.split(',')

      // Get class/teacher/classroom from URL
      if (type === 'classes' && data.some(elem => (StorageModule.classList || []).includes(elem))) {
        StateModule.setCurrentEntity({
          type: EntityType.Class,
          data
        })
      } else if (type === 'teachers' && data.some(elem => (StorageModule.teacherList || []).includes(elem))) {
        StateModule.setCurrentEntity({
          type: EntityType.Teacher,
          data
        })
      } else if (type === 'classrooms' && data.some(elem => (StorageModule.classroomList || []).includes(elem))) {
        StateModule.setCurrentEntity({
          type: EntityType.Classroom,
          data
        })
      } else if (type === 'classrooms' && data.includes('empty')) {
        StateModule.setCurrentEntity({
          type: EntityType.EmptyClassrooms,
          data: ['empty']
        })

        // Show 404 page if class/teacher/classroom is not found
      } else {
        await this.$router.replace({ name: 'notfound', params: { 0: this.$route.fullPath } })
        return
      }

      // Show 404 page if route is incomplete
    } else if (this.$route.params.type && !this.$route.params.value) {
      await this.$router.replace({ name: 'notfound', params: { 0: this.$route.fullPath } })
      return

      // Try to get stored entity
    } else {
      // Get class/teacher/classroom from settings
      if (SettingsModule.selectedEntity) {
        const selectedEntity = SettingsModule.selectedEntity
        const entityValue = selectedEntity.data.join(',')

        let entityType
        switch (selectedEntity.type) {
          case EntityType.Class:
            entityType = 'classes'
            break
          case EntityType.Teacher:
            entityType = 'teachers'
            break
          case EntityType.Classroom:
          case EntityType.EmptyClassrooms:
            entityType = 'classrooms'
            break
        }

        await this.$router.replace({
          name: 'timetable',
          params: { type: entityType, value: entityValue, skipListUpdate: '1' }
        })

        // Show welcome page if class/teacher/classroom is not stored
      } else {
        await this.$router.replace({ name: 'welcome' })
      }

      return
    }

    // Set page title
    const currentEntity = StateModule.currentEntity
    const entityNice = currentEntity?.type !== EntityType.EmptyClassrooms ? currentEntity?.data.join(', ') : 'Proste učilnice'

    document.title = process.env.VUE_APP_TITLE + ' – ' + entityNice
    this.$emit('setPageTitle', 'Urnik – ' + entityNice)

    // Set that timetable is ready
    this.isReady = true

    // Update data
    if (currentEntity?.type === EntityType.EmptyClassrooms) {
      await StorageModule.updateEmptyClassrooms()
    } else {
      if (SettingsModule.showSubstitutions) {
        const timetableUpdate = StorageModule.updateTimetable()
        const substitutionsUpdates = StorageModule.updateSubstitutions()
        await Promise.all([timetableUpdate, substitutionsUpdates])
      } else {
        await StorageModule.updateTimetable()
      }
    }
  }
}
</script>
