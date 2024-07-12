<script setup lang="ts">
import {
  mdiCog,
  mdiFileDocumentOutline,
  mdiFood,
  mdiNewspaper,
  mdiRss,
  mdiTimetable,
} from '@mdi/js'
import { useSwipe } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import PullToRefresh from 'pulltorefreshjs'
import { computed, defineAsyncComponent, onMounted, ref, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useDisplay, useTheme } from 'vuetify'

import AppSnackbar from '@/components/AppSnackbar.vue'
import NavigationDay from '@/components/NavigationDay.vue'
import NavigationDesktop from '@/components/NavigationDesktop.vue'
import NavigationMobile from '@/components/NavigationMobile.vue'
import { useSessionStore } from '@/stores/session'
import { ThemeType, useSettingsStore } from '@/stores/settings'
import { updateAllData } from '@/utils/update'

// Dynamically import navigation components so mobile layout is not loaded on desktop
// TODO: Check if this is useful
// const NavigationDesktop = defineAsyncComponent(() => import('@/components/NavigationDesktop.vue'))
// const NavigationMobile = defineAsyncComponent(() => import('@/components/NavigationMobile.vue'))
// const NavigationDay = defineAsyncComponent(() => import('@/components/NavigationDay.vue'))

const router = useRouter()
const { mobile } = useDisplay()
const theme = useTheme()

// TODO - bheck below
const { entityList } = storeToRefs(useSessionStore())
const userStore = useSessionStore()
const { resetEntityToSettings } = userStore
resetEntityToSettings()

const { enablePullToRefresh, themeType } = storeToRefs(useSettingsStore())

const routerTitle = computed(() => router.currentRoute.value.meta.title)
const routerName = computed(() => router.currentRoute.value.name)

// TODO: Check if these properties should be more descriptive (like showNavigation) or based on route names (like timetableOrMenu)
// TODO: Also check if these properties should be defined in route meta
const welcome = computed(() => routerName.value === 'welcome')
// We show entity name on timetable and menu views, because they are dependent on the current entity
// Timetable obviously depends on the entity, and menu depends on the entity to show a lunch schedule
const timetableOrMenu = () => routerName.value === 'timetable' || routerName.value === 'menu'
const showEntityName = computed(timetableOrMenu)
const showDayNavigation = computed(timetableOrMenu)

onMounted(() => {
  PullToRefresh.init({
    mainElement: '#ptr--target',
    triggerElement: '#main',

    instructionsPullToRefresh: 'Povlecite za posodobitev',
    instructionsReleaseToRefresh: 'Izpustite za posodobitev',
    instructionsRefreshing: 'Posodabljanje',

    // TODO: Disable PTR on settings, sources, etc.
    shouldPullToRefresh: () => enablePullToRefresh.value && !window.scrollY,
    onRefresh: (): void => {
      // TODO: This doesn't reload substitutions properly
      updateAllData()
    },
  })

  // displaySnackbar('Nova posodobitev', 'Posodobi', () => (show.value = false), -1)

  // Set theme
  // TODO
  // if (themeType.value === ThemeType.System) {
  //   theme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  //     ? 'darkTheme'
  //     : 'lightTheme'
  //   return
  // }

  // theme.global.name.value = themeType.value
})

const pages: { title: string; link: string; icon: string }[] = [
  { title: 'Viri', link: 'sources', icon: mdiFileDocumentOutline },
  { title: 'Naročanje', link: 'subscribe', icon: mdiRss },
  // { title: 'Nastavitve', link: 'settings', icon: mdiCog },
]

const navigation: { title: string; link: string; icon: string }[] = [
  // { title: 'Urnik', link: 'timetable', icon: mdiTimetable },
  { title: 'Jedilnik', link: 'menu', icon: mdiFood },
  { title: 'Okrožnice', link: 'circulars', icon: mdiNewspaper },
]
</script>

<template>
  <v-app>
    <v-app-bar class="pr-2">
      <v-app-bar-title>
        <div>{{ routerTitle }}</div>
        <div v-if="showEntityName" class="entities">
          {{ entityList.join(', ') }}
        </div>
      </v-app-bar-title>
      <div v-if="!welcome" role="navigation">
        <v-btn-icon
          v-for="page in pages"
          :key="page.link"
          :alt="page.title"
          :title="page.title"
          :aria-label="page.title"
          :icon="page.icon"
          :to="{ name: page.link }"
        />
      </div>
      <template v-if="mobile && showDayNavigation" #extension>
        <NavigationDay />
      </template>
    </v-app-bar>
    <NavigationDesktop v-if="!mobile && !welcome" :navigation="navigation" />
    <v-main id="main">
      <div id="ptr--target" />
      <v-container fluid class="h-100">
        <router-view />
      </v-container>
    </v-main>
    <AppSnackbar />
    <NavigationMobile v-if="mobile && !welcome" :navigation="navigation" />
  </v-app>
</template>

<style>
.entities {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}
</style>
