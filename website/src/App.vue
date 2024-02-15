<script setup lang="ts">
import AppSnackbar from '@/components/AppSnackbar.vue'
import NavigationDay from '@/components/NavigationDay.vue'
import NavigationDesktop from '@/components/NavigationDesktop.vue'
import NavigationMobile from '@/components/NavigationMobile.vue'
import { ThemeType, useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { updateAllData } from '@/utils/update'
import { useSwipe } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import PullToRefresh from 'pulltorefreshjs'
import { computed, onMounted, ref, watch } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useDisplay, useTheme } from 'vuetify'

const router = useRouter()
const { mobile } = useDisplay()
const theme = useTheme()

const { entities, day } = storeToRefs(useUserStore())
const userStore = useUserStore()
const { resetEntityToSettings } = userStore
resetEntityToSettings()

const { enablePullToRefresh, themeType } = storeToRefs(useSettingsStore())

const routerTitle = computed(() => router.currentRoute.value.meta.title)
const routerName = computed(() => router.currentRoute.value.name)
const welcome = computed(() => routerName.value === 'welcome')
const showDayNavigation = computed(
  () => routerName.value === 'timetable' || routerName.value === 'menu',
)

const swipe = ref(null)
const { direction } = useSwipe(swipe)

watch(direction, () => {
  switch (direction.value) {
    case 'left':
      day.value = Math.min(4, day.value + 1)
      break
    case 'right':
      day.value = Math.max(0, day.value - 1)
      break
  }
})

onMounted(() => {
  PullToRefresh.init({
    mainElement: '#ptr--target',
    triggerElement: '#main',

    instructionsPullToRefresh: 'Povlecite za posodobitev',
    instructionsReleaseToRefresh: 'Izpustite za posodobitev',
    instructionsRefreshing: 'Posodabljanje',

    shouldPullToRefresh: () => enablePullToRefresh.value && !window.scrollY,
    onRefresh: (): void => {
      updateAllData()
    },
  })

  // displaySnackbar('Nova posodobitev', 'Posodobi', () => (show.value = false), -1)

  // Set theme
  if (themeType.value === ThemeType.System) {
    theme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'darkTheme'
      : 'lightTheme'
    return
  }

  theme.global.name.value = themeType.value
})

const pages: { title: string; link: string; icon: string }[] = [
  { title: 'Viri', link: 'sources', icon: 'mdi-file-document-outline' },
  { title: 'Naročanje', link: 'subscribe', icon: 'mdi-rss' },
  { title: 'Nastavitve', link: 'settings', icon: 'mdi-cog' },
]

const navigation: { title: string; link: string; icon: string }[] = [
  { title: 'Urnik', link: 'timetable', icon: 'mdi-timetable' },
  { title: 'Jedilnik', link: 'menu', icon: 'mdi-food' },
  { title: 'Okrožnice', link: 'circulars', icon: 'mdi-newspaper' },
]
</script>

<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-title>
        <div @click="resetEntityToSettings()">{{ routerTitle }}</div>
        <div v-if="routerName === 'timetable'" class="entities">
          {{ entities.join(', ') }}
        </div>
      </v-app-bar-title>
      <div v-if="!welcome">
        <v-btn-icon
          v-for="page in pages"
          :key="page.title"
          :alt="page.title"
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
    <v-main id="main" ref="swipe">
      <span id="ptr--target"></span>
      <v-container fluid><router-view /></v-container>
    </v-main>
    <AppSnackbar />
    <NavigationMobile v-if="mobile && !welcome" :navigation="navigation" />
  </v-app>
</template>
<style>
.entities {
  font-size: 0.775rem;
  color: rgba(255, 255, 255, 0.6);
}

.ptr--icon,
.ptr--text {
  color: rgb(var(--v-theme-text)) !important;
}
</style>
