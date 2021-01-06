<template>
  <v-app>
    <v-app-bar app clipped-left color="#009300" dark extension-height="35">
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

      <template v-if="isNavigationDisplayed && isMobile && isDayMenuDisplayed" v-slot:extension>
        <day-navigation />
      </template>
    </v-app-bar>

    <view-navigation-desktop v-if="!isMobile" />

    <v-main id="main" v-bind:class="{ 'pb-16': isNavigationDisplayed && isMobile }">
      <span id="ptr--target"></span>

      <v-container fluid>
        <router-view @setDayMenuDisplay=setDayMenuDisplay
          @setNavigationDisplay=setNavigationDisplay
          @setPageTitle=setPageTitle
          @setPullToRefreshAllowed=setPullToRefreshAllowed />
      </v-container>
    </v-main>

    <v-snackbar v-model="isSnackbarDisplayed">
      {{ snackbarMessage }}
    </v-snackbar>

    <view-navigation-mobile v-if="isNavigationDisplayed && isMobile" />
  </v-app>
</template>

<style lang="scss">
// Hide scrollbar that Vuetify adds by default
html {
  overflow-y: auto !important;
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
import PullToRefresh from 'pulltorefreshjs'
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'
import { updateAllData } from '@/store/modules/storage'

@Component({
  components: {
    ViewNavigationDesktop: () => import(/* webpackChunkName: "desktop" */ '@/components/navigation/ViewNavigationDesktop.vue'),
    ViewNavigationMobile: () => import(/* webpackChunkName: "mobile" */ '@/components/navigation/ViewNavigationMobile.vue'),
    DayNavigation: () => import(/* webpackChunkName: "mobile" */ '@/components/navigation/DayNavigation.vue')
  }
})
export default class App extends Vue {
  mdiCog = mdiCog

  pageTitle = process.env.VUE_APP_TITLE
  isPullToRefreshAllowed = true
  isNavigationDisplayed = true
  isDayMenuDisplayed = false

  isSnackbarDisplayed = false
  snackbarMessage = ''

  get isMobile (): boolean {
    return this.$vuetify.breakpoint.width < 1064
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  snackbarHandler (event: Event): any {
    this.snackbarMessage = (event as CustomEvent).detail.message
    this.isSnackbarDisplayed = true
  }

  mounted (): void {
    // Event listener for displaying snackbars
    document.addEventListener('displaySnackbar', this.snackbarHandler)

    // Create pull to refresh
    PullToRefresh.init({
      mainElement: '#ptr--target',
      triggerElement: 'body',

      instructionsPullToRefresh: 'Povlecite za posodobitev',
      instructionsReleaseToRefresh: 'Izpustite za posodobitev',
      instructionsRefreshing: 'Posodabljanje',

      shouldPullToRefresh: () => !window.scrollY && this.isPullToRefreshAllowed && SettingsModule.enablePullToRefresh,
      onRefresh: (): void => {
        updateAllData()
      }
    })
  }

  destroyed (): void {
    // Remove event listener for displaying snackbars
    document.removeEventListener('displaySnackbar', this.snackbarHandler)

    // Destroy pull to refresh instances
    PullToRefresh.destroyAll()
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
