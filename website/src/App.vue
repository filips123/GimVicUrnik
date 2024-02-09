<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'

import { RouterView, useRouter } from 'vue-router'
import { useDisplay, useTheme } from 'vuetify'

import { useUserStore } from '@/stores/user'
import { useSettingsStore, ThemeType } from '@/stores/settings'

import { sortEntityList } from '@/composables/entities'
import { updateAllData } from '@/composables/update'

import PullToRefresh from 'pulltorefreshjs'

import NavigationDay from '@/components/NavigationDay.vue'
import NavigationDesktop from '@/components/NavigationDesktop.vue'
import Snackbar from '@/components/Snackbar.vue'
import NavigationMobile from '@/components/NavigationMobile.vue'

const { mobile } = useDisplay()
const theme = useTheme()

const router = useRouter()
const routerTitle = computed(() => router.currentRoute.value.meta.title)
const routerName = computed(() => router.currentRoute.value.name)

const userStore = useUserStore()
const { entities, entityType } = storeToRefs(useUserStore())
const { enablePullToRefresh, themeType } = storeToRefs(useSettingsStore())

userStore.resetEntityToSettings()

const sortedEntityList = computed(() => sortEntityList(entityType.value, entities.value))

onMounted(() => {
  PullToRefresh.init({
    mainElement: '#ptr--target',

    instructionsPullToRefresh: 'Povlecite za posodobitev',
    instructionsReleaseToRefresh: 'Izpustite za posodobitev',
    instructionsRefreshing: 'Posodabljanje',

    shouldPullToRefresh: () => enablePullToRefresh.value && !window.scrollY,
    onRefresh: (): void => {
      updateAllData()
    },
  })

  // Set theme - here for now
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
  { title: 'Jedilnik', link: 'menus', icon: 'mdi-food' },
  { title: 'Okrožnice', link: 'circulars', icon: 'mdi-newspaper' },
]

const welcome = computed(() => {
  return routerName.value === 'welcome'
})
</script>

<template>
  <v-app>
    <v-app-bar app clipped-left extension-height="35">
      <v-app-bar-title>
        <span @click="userStore.resetEntityToSettings()">{{ routerTitle }}</span>
        <template v-if="routerTitle === 'Urnik'">
          <div class="entities">
            {{ sortedEntityList.join(', ') }}
          </div>
        </template>
      </v-app-bar-title>
      <template v-if="!welcome">
        <v-btn-icon
          v-for="page in pages"
          :to="{ name: page.link }"
          :alt="page.title"
          :aria-label="page.title"
          :icon="page.icon"
        />
      </template>
      <template
        v-if="mobile && (routerName === 'timetable' || routerName === 'menus')"
        v-slot:extension
      >
        <NavigationDay />
      </template>
    </v-app-bar>
    <NavigationDesktop v-if="!mobile && !welcome" :navigation="navigation" />
    <v-main id="main">
      <span class="bg-primary" id="ptr--target"></span>
      <v-container fluid><router-view /></v-container>
    </v-main>
    <Snackbar />
    <NavigationMobile v-if="mobile && !welcome" :navigation="navigation" />
  </v-app>
</template>
