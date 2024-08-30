<script setup lang="ts">
import {
  mdiCog,
  mdiFileDocumentOutline,
  mdiFood,
  mdiNewspaper,
  mdiRss,
  mdiTimetable,
} from '@mdi/js'
import { usePreferredDark } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import PullToRefresh from 'pulltorefreshjs'
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useDisplay, useTheme } from 'vuetify'

import AppSnackbar from '@/components/AppSnackbar.vue'
import NavigationDay from '@/components/NavigationDay.vue'
import NavigationDesktop from '@/components/NavigationDesktop.vue'
import NavigationMobile from '@/components/NavigationMobile.vue'
import { useSessionStore } from '@/stores/session'
import { ThemeType, useSettingsStore } from '@/stores/settings'
import { updateAllData } from '@/utils/update'

const router = useRouter()
const { mobile } = useDisplay()
const theme = useTheme()

const { currentEntityList } = storeToRefs(useSessionStore())
const { themeType, enablePullToRefresh } = storeToRefs(useSettingsStore())

const routerTitle = computed(() => router.currentRoute.value.meta.title)

const allowPullToRefresh = computed(() => !!router.currentRoute.value.meta.allowPullToRefresh)
const showEntityName = computed(() => !!router.currentRoute.value.meta.showEntityName)
const showDayTabs = computed(() => !!router.currentRoute.value.meta.showDayTabs)

onMounted(() => {
  PullToRefresh.init({
    mainElement: '#ptr--target',
    triggerElement: '#main',

    instructionsPullToRefresh: 'Povlecite za posodobitev',
    instructionsReleaseToRefresh: 'Izpustite za posodobitev',
    instructionsRefreshing: 'Posodabljanje',

    shouldPullToRefresh: () =>
      enablePullToRefresh.value && allowPullToRefresh.value && !window.scrollY,
    onRefresh: (): void => {
      updateAllData()
    },
  })
})

onUnmounted(() => {
  PullToRefresh.destroyAll()
})

watch(
  [themeType, usePreferredDark()],
  ([themeType, prefersDark]) => {
    if (themeType === ThemeType.System) {
      theme.global.name.value = prefersDark ? 'dark' : 'light'
    } else {
      theme.global.name.value = themeType
    }
  },
  { immediate: true },
)

const pages: { title: string; link: string; icon: string }[] = [
  { title: 'Viri', link: 'sources', icon: mdiFileDocumentOutline },
  { title: 'Naročanje', link: 'subscribe', icon: mdiRss },
  { title: 'Nastavitve', link: 'settings', icon: mdiCog },
]

const navigation: { title: string; link: string; icon: string }[] = [
  { title: 'Urnik', link: 'timetable', icon: mdiTimetable },
  { title: 'Jedilnik', link: 'menu', icon: mdiFood },
  { title: 'Okrožnice', link: 'circulars', icon: mdiNewspaper },
]
</script>

<template>
  <v-app>
    <v-app-bar class="app-bar pr-2">
      <v-app-bar-title>
        <h1 class="app-title">{{ routerTitle }}</h1>
        <div v-if="showEntityName" class="app-subtitle">{{ currentEntityList.join(', ') }}</div>
      </v-app-bar-title>
      <div role="navigation">
        <v-btn-icon
          v-for="page in pages"
          :key="page.link"
          :alt="page.title"
          :title="page.title"
          :aria-label="page.title"
          :icon="page.icon"
          :to="{ name: page.link }"
          class="ml-1"
        />
      </div>
      <template v-if="mobile && showDayTabs" #extension>
        <NavigationDay />
      </template>
    </v-app-bar>
    <NavigationDesktop v-if="!mobile" :navigation="navigation" />
    <v-main id="main">
      <div id="ptr--target"></div>
      <v-container fluid class="h-100">
        <router-view />
      </v-container>
    </v-main>
    <NavigationMobile v-if="mobile" :navigation="navigation" />
    <AppSnackbar />
  </v-app>
</template>

<style>
/* Set styles for app title and subtitle */

.app-bar {
  user-select: none;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 500;
  letter-spacing: 0.0125em;
  text-overflow: ellipsis;
  overflow-x: hidden;
}

.app-subtitle {
  font-size: 0.9rem;
  color: rgba(var(--v-theme-on-primary), var(--v-app-subtitle-opacity));
  text-overflow: ellipsis;
  overflow-x: auto;
  scrollbar-width: none;
}

/* Fix pull to refresh colors in dark theme */

.ptr--icon,
.ptr--text {
  color: rgb(var(--v-theme-on-background)) !important;
}
</style>
