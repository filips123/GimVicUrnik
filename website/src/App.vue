<template>
  <v-app>
    <v-app-bar app color="#009300" dark extension-height="35">
      <div class="d-flex align-center">
        <v-img alt="GimVičUrnik Logo"
          class="shrink mr-2"
          contain
          src="./assets/logo.png"
          transition="scale-transition"
          width="40" />
        <v-toolbar-title>{{ pageTitle }}</v-toolbar-title>
      </div>

      <v-spacer />

      <v-btn v-if="isNavigationDisplayed" :to="{ name: 'settings' }" alt="Nastavitve" icon large>
        <v-icon>{{ mdiCog }}</v-icon>
      </v-btn>

      <template v-if="isNavigationDisplayed && isDayMenuDisplayed" v-slot:extension>
        <day-navigation />
      </template>
    </v-app-bar>

    <!-- TODO: Desktop layout without day navigation and with side navigation instead of bottom one -->

    <v-main id="main" v-bind:class="{ 'pb-16': isNavigationDisplayed }">
      <v-container fluid>
        <router-view @setDayMenuDisplay=setDayMenuDisplay
          @setNavigationDisplay=setNavigationDisplay
          @setPageTitle=setPageTitle
          @setPullToRefreshAllowed=setPullToRefreshAllowed />
      </v-container>
    </v-main>

    <view-navigation v-if="isNavigationDisplayed" />
  </v-app>
</template>

<style lang="scss">
// Hide scrollbar that Vuetify adds by default
html {
  overflow-y: auto;
}

// Disable native pull-to-refresh and Safari elastic scrolling
html, body {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}

// Reverse switch and label
.v-input--reverse .v-input__slot {
  flex-direction: row-reverse;
  justify-content: flex-end;

  .v-application--is-ltr & {
    .v-input--selection-controls__input {
      margin-left: 8px;
      margin-right: 0;
    }
  }

  .v-application--is-rtl & {
    .v-input--selection-controls__input {
      margin-left: 0;
      margin-right: 8px;
    }
  }
}

// Move switch and label more to the top
.v-input--switch {
  margin-bottom: -25px;
  margin-top: 0;
}
</style>

<script lang="ts">
import { mdiCog } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import DayNavigation from '@/components/navigation/DayNavigation.vue'
import ViewNavigation from '@/components/navigation/ViewNavigation.vue'

@Component({
  components: { ViewNavigation, DayNavigation }
})
export default class App extends Vue {
  mdiCog = mdiCog

  pageTitle = process.env.VUE_APP_TITLE
  isPullToRefreshAllowed = true
  isNavigationDisplayed = true
  isDayMenuDisplayed = false

  mounted (): void {
    // TODO: Set up pull to refresh
  }

  destroyed (): void {
    // TODO: Destroy pull to refresh instances
  }

  setPageTitle (pageTitle: string): void {
    this.pageTitle = pageTitle
  }

  setPullToRefreshAllowed (isPullToRefreshAllowed: boolean): void {
    this.isPullToRefreshAllowed = isPullToRefreshAllowed
  }

  setNavigationDisplay (isNavigationDisplayed: boolean): void {
    this.isNavigationDisplayed = isNavigationDisplayed
  }

  setDayMenuDisplay (isDayMenuDisplayed: boolean): void {
    this.isDayMenuDisplayed = isDayMenuDisplayed
  }
}
</script>
