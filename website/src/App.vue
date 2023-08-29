<template>
  <v-app>
    <v-app-bar app clipped-left color="#009300" dark extension-height="35">
      <div class="d-flex align-center overflow-x-hidden pr-1">
        <router-link title="Domov" :to="{ name: 'home' }">
          <v-img alt="GimVičUrnik Logo"
            class="mr-2"
            src="./assets/logo.svg"
            width="40" />
        </router-link>
        <v-toolbar-title>{{ pageTitle }}</v-toolbar-title>
      </div>

      <v-spacer />

      <v-btn v-if="isNavigationDisplayed"
        :to="{ name: 'subscribe' }"
        alt="Naročanje"
        aria-label="Naročanje"
        class="mr-1"
        icon
        large>
        <v-icon>{{ mdiRss }}</v-icon>
      </v-btn>

      <v-btn v-if="isNavigationDisplayed"
        :to="{ name: 'settings' }"
        alt="Nastavitve"
        aria-label="Nastavitve"
        class="mr-n2"
        icon
        large>
        <v-icon>{{ mdiCog }}</v-icon>
      </v-btn>

      <template v-if="isNavigationDisplayed && isMobile && isDayMenuDisplayed" v-slot:extension>
        <day-navigation />
      </template>
    </v-app-bar>

    <view-navigation-desktop v-if="isNavigationDisplayed && !isMobile" />

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

      <template v-if="snackbarButton" v-slot:action="{ attrs }">
        <v-btn v-bind="attrs" color="green" text @click="snackbarAction()">
          {{ snackbarButton }}
        </v-btn>
      </template>
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

// Move snackbar a bit more to the top so it doesn't hide navigation
.v-snack {
  padding-bottom: 60px !important;
}
</style>

<script lang="ts">
import { mdiCog, mdiRss } from '@mdi/js'
import PullToRefresh from 'pulltorefreshjs'
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule, ThemeType } from '@/store/modules/settings'
import { updateAllData } from '@/store/modules/storage'
import { displaySnackbar, hideSnackbar } from '@/utils/snackbar'

@Component({
  components: {
    ViewNavigationDesktop: () => import(/* webpackChunkName: "desktop" */ '@/components/navigation/ViewNavigationDesktop.vue'),
    ViewNavigationMobile: () => import(/* webpackChunkName: "mobile" */ '@/components/navigation/ViewNavigationMobile.vue'),
    DayNavigation: () => import(/* webpackChunkName: "mobile" */ '@/components/navigation/DayNavigation.vue')
  }
})
export default class App extends Vue {
  mdiCog = mdiCog
  mdiRss = mdiRss

  pageTitle = process.env.VUE_APP_TITLE
  isPullToRefreshAllowed = true
  isNavigationDisplayed = true
  isDayMenuDisplayed = false

  isSnackbarDisplayed = false
  snackbarMessage = ''
  snackbarButton = ''
  snackbarAction?: () => void

  get isMobile (): boolean {
    return this.$vuetify.breakpoint.width < 1064
  }

  snackbarHandler (event: Event): void {
    if (!(event as CustomEvent).detail) {
      this.isSnackbarDisplayed = false
      return
    }

    if (this.isSnackbarDisplayed) return

    this.snackbarMessage = (event as CustomEvent).detail.message
    this.snackbarButton = (event as CustomEvent).detail?.button
    this.snackbarAction = (event as CustomEvent).detail?.action

    this.isSnackbarDisplayed = true
  }

  themeHandler (event: MediaQueryListEvent): void {
    // Change Vuetify theme to match system theme
    if (SettingsModule.theme === ThemeType.System) {
      this.$vuetify.theme.dark = event.matches
    }

    // Also set body color to make it possible for browser to style scrollbars
    setTimeout(() => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      document.getElementsByTagName('body')[0].style.background = getComputedStyle(document.getElementById('app'))['background-color']
    }, 0)
  }

  swUpdatedHandler (event: Event): void {
    const registration: ServiceWorkerRegistration = (event as CustomEvent).detail

    displaySnackbar('Na voljo je posodobitev', 'Posodobi', () => {
      hideSnackbar()

      if (!registration || !registration.waiting) return
      registration.waiting.postMessage({ type: 'SKIP_WAITING' })
    })
  }

  controllerChangedHandler (): void {
    // Add GET parameter to invalidate cache of index HTML file
    window.location.href = location.protocol + '//' + location.host + '?updated=' + (new Date()).getTime()
  }

  created (): void {
    // Event listeners for displaying and hiding snackbars
    document.addEventListener('displaySnackbar', this.snackbarHandler)
    document.addEventListener('hideSnackbar', this.snackbarHandler)

    // Event listener for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    if (typeof mediaQuery.addEventListener === 'undefined') mediaQuery.addListener(this.themeHandler)
    else mediaQuery.addEventListener('change', this.themeHandler)

    // Event listener for detecting service worker updates
    document.addEventListener('serviceWorkerUpdated', this.swUpdatedHandler, { once: true })

    // Event listener for detecting controller changes
    navigator.serviceWorker && navigator.serviceWorker.addEventListener('controllerchange', this.controllerChangedHandler, { once: true })
  }

  mounted (): void {
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

    // Also set body color to make it possible for browser to style scrollbars
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    document.getElementsByTagName('body')[0].style.background = getComputedStyle(document.getElementById('app'))['background-color']
  }

  destroyed (): void {
    // Remove event listeners for displaying and hiding snackbars
    document.removeEventListener('displaySnackbar', this.snackbarHandler)
    document.removeEventListener('hideSnackbar', this.snackbarHandler)

    // Remove event listener for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', this.themeHandler)

    // Remove event listener for detecting service worker updates
    document.removeEventListener('serviceWorkerUpdated', this.swUpdatedHandler)

    // Remove event listener for detecting controller changes
    navigator.serviceWorker && navigator.serviceWorker.removeEventListener('controllerchange', this.controllerChangedHandler)

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
