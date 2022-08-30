<!-- Component for displaying navigation between timetable/menus/documents views on desktop -->

<template>
  <v-navigation-drawer :mini-variant="!isNavigationExpanded" app clipped mini-variant-width="72" permanent>
    <v-list rounded class="pt-6">
      <v-list-item link :to="{ name: 'timetable' }" aria-label="Urnik">
        <v-list-item-icon>
          <v-icon>{{ mdiTimetable }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>Urnik</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item link :to="{ name: 'menus' }" aria-label="Jedilnik">
        <v-list-item-icon>
          <v-icon>{{ mdiFood }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>Jedilnik</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item link :to="{ name: 'documents' }" aria-label="Okrožnice">
        <v-list-item-icon>
          <v-icon>{{ mdiNewspaper }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>Okrožnice</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>

    <template v-slot:append>
      <v-list-item link @click="isNavigationExpanded = !isNavigationExpanded">
        <v-list-item-icon>
          <v-icon>{{ isNavigationExpanded ? mdiChevronLeft : mdiChevronRight }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title></v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </v-navigation-drawer>
</template>

<style lang="scss">
// Fix jumping icons caused by closing expanded navigation drawer
.v-navigation-drawer--custom-mini-variant {
  .v-list-item {
    justify-content: unset !important;
  }
}
</style>

<script lang="ts">
import { mdiChevronLeft, mdiChevronRight, mdiFood, mdiNewspaper, mdiTimetable } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class ViewNavigationDesktop extends Vue {
  mdiTimetable = mdiTimetable
  mdiFood = mdiFood
  mdiNewspaper = mdiNewspaper

  mdiChevronRight = mdiChevronRight
  mdiChevronLeft = mdiChevronLeft

  isNavigationExpanded = false
}
</script>
