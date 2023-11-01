<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useDisplay } from 'vuetify'

import NavigationDesktop from '@/components/NavigationDesktop.vue'
import NavigationMobile from '@/components/NavigationMobile.vue'
import NavigationDay from '@/components/NavigationDay.vue'

import { updateAllData } from './composables/update'

// TODO: Check for tablet
const { mobile } = useDisplay()

// Not fast enough / need to check again?
updateAllData()

const pages: { title: string; link: string; icon: string }[] = [
  { title: 'Viri', link: 'sources', icon: 'mdi-file-document-outline' },
  { title: 'Naročanje', link: 'subscribe', icon: 'mdi-rss' },
  { title: 'Nastavitve', link: 'settings', icon: 'mdi-cog' }
]

// Props
const navigation: { title: string; link: string; icon: string }[] = [
  { title: 'Urnik', link: 'timetable', icon: 'mdi-timetable' },
  { title: 'Jedilnik', link: 'menus', icon: 'mdi-food' },
  { title: 'Okrožnice', link: 'circulars', icon: 'mdi-newspaper' }
]

const weekdays = ['Ponedeljek', 'Torek', 'Sreda', 'Četrtek', 'Petek']

/* IGNORE FOR NOW */

/*

Get router in script
Break mobile and desktop in right breakpoint!

import PullToRefresh from 'pulltorefreshjs'
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule, ThemeType } from '@/store/modules/settings'
import { updateAllData } from '@/store/modules/storage'
import { displaySnackbar, hideSnackbar } from '@/utils/snackbar'

pageTitle = process.env.VUE_APP_TITLE
isPullToRefreshAllowed = true
isNavigationDisplayed = true
isDayMenuDisplayed = false
isSnackbarDisplayed = false
snackbarMessage = ''
snackbarButton = ''
snackbarAction?: () => void
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

*/
</script>

<template>
  <v-app>
    <v-app-bar app clipped-left color="#009300" dark extension-height="35">
      <v-app-bar-title>{{ $router.currentRoute.value.meta.title }}</v-app-bar-title>

      <v-btn
        v-for="page in pages"
        :to="{ name: page.link }"
        :alt="page.title"
        :aria-label="page.title"
        :icon="page.icon"
        large
      />

      <template v-if="mobile" v-slot:extension>
        <navigation-day :weekdays="weekdays" />
      </template>
    </v-app-bar>

    <navigation-desktop v-if="!mobile" :navigation="navigation" />

    <v-main id="main" :class="{ 'pb-16': !mobile }">
      <!--<span id="ptr--target"></span>-->

      <v-container fluid>
        <router-view :mobile="mobile" />
      </v-container>
    </v-main>

    <!--
    <v-snackbar v-model="isSnackbarDisplayed">
      {{ snackbarMessage }}

      <template v-if="snackbarButton" v-slot:action="{ attrs }">
        <v-btn v-bind="attrs" color="green" text @click="snackbarAction()">
          {{ snackbarButton }}
        </v-btn>
      </template>
    </v-snackbar>
    -->

    <navigation-mobile v-if="mobile" :navigation="navigation" />
  </v-app>
</template>

<style>
/* IGNORE FOR NOW */

/* Hide scrollbar that Vuetify adds by default */

html {
  overflow-y: auto !important;
}

/*Disable native pull-to-refresh and Safari elastic scrolling */
html,
body {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior-y: contain;
}

/* Reverse switch and label */
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

/* Move switch and label more to the top */
.v-input--switch {
  margin-bottom: -25px;
  margin-top: 0;
}

/* Move snackbar a bit more to the top so it doesn't hide navigation */
.v-snack {
  padding-bottom: 60px !important;
}
</style>
