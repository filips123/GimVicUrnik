<template>
  <v-row v-if="$root.$children[0].isMobile" class="menus" justify="center">
    <v-tabs-items ref="tabs" v-model="currentDay" :touch="tabsItemsTouch">
      <v-tab-item v-for="(dayName, dayIndex) in daysInWeek" :key="dayIndex">
        <menu-display v-if="dayIndex in documents"
          :date="documents[dayIndex].date"
          :lunch-schedule="documents[dayIndex].lunchSchedule"
          :menu="documents[dayIndex].menu"
          class="ma-3"
          mobile="1" />
      </v-tab-item>
    </v-tabs-items>
  </v-row>

  <v-row v-else no-gutters>
    <v-col v-for="(value, index) in documents" :key="value.date">
      <menu-display :class="{ 'ml-2 ml-lg-5': 0 < index, 'ml-3 ml-lg-6': index === 0, 'mr-3 mr-lg-6': index === documents.length - 1 }"
        :date="value.date"
        :lunch-schedule="value.lunchSchedule"
        :menu="value.menu"
        class="mt-0 mt-md-6" />
    </v-col>
  </v-row>
</template>

<style lang="scss">
// Fix background on dark theme and resize mobile menus
.menus > .v-tabs-items {
  background-color: unset !important;
  width: 100%;
}

// Fix menus height and width
.v-window__container {
  height: inherit !important;
  width: inherit !important;
}
</style>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import MenuDisplay from '@/components/menus/MenuDisplay.vue'
import { StateModule } from '@/store/modules/state'
import { LunchSchedule, Menu, StorageModule } from '@/store/modules/storage'
import { daysInWeek } from '@/utils/days'

@Component({
  components: { MenuDisplay }
})
export default class Menus extends Vue {
  daysInWeek = daysInWeek

  // Custom touch function which does not stop propagation
  // This is needed for pull to refresh to work
  tabsItemsTouch = {
    left: (): void => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      this.$vuetify.rtl ? this.$refs.tabs.prev() : this.$refs.tabs.next()
    },
    right: (): void => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      this.$vuetify.rtl ? this.$refs.tabs.next() : this.$refs.tabs.prev()
    },
    end: (): void => undefined,
    start: (): void => undefined
  }

  get currentDay (): number {
    return StateModule.currentDay
  }

  set currentDay (currentDay: number) {
    StateModule.setCurrentDay(currentDay)
  }

  get documents (): { date: string, lunchSchedule: LunchSchedule[], menu: Menu }[] {
    if (!StorageModule.lunchSchedule || !StorageModule.menus) return []

    const data: { date: string, lunchSchedule: LunchSchedule[], menu: Menu }[] = []
    for (let i = 0; i < (StorageModule.lunchSchedule.length || 0); i++) {
      const date = StorageModule.lunchSchedule[i][0]
      const lunchSchedule = StorageModule.lunchSchedule[i][1]
      const menu = StorageModule.menus[i][1]

      data.push({ date, lunchSchedule, menu })
    }

    return data
  }

  created (): void {
    document.title = process.env.VUE_APP_TITLE + ' – Jedilnik'
    this.$emit('setPageTitle', 'Jedilnik')

    this.$emit('setDayMenuDisplay', true)

    StorageModule.updateLunchSchedule()
    StorageModule.updateMenus()
  }
}
</script>
