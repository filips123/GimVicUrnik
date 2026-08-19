<script setup lang="ts">
import { mdiLogout, mdiTrophy } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { computed, defineAsyncComponent, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'

import { useSnackbarStore } from '@/composables/snackbar'
import { sportNames, type SportSlug, useSportsStore } from '@/stores/sports'
import { getCurrentDate, getISODate } from '@/utils/days'

const SportsSchedule = defineAsyncComponent(() => import('@/components/SportsSchedule.vue'))
const SportsTournament = defineAsyncComponent(() => import('@/components/SportsTournament.vue'))

type SportsSection = SportSlug | 'schedule'

const route = useRoute()
const router = useRouter()
const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const { mobile } = useDisplay()
const { seasons, admin } = storeToRefs(sportsStore)

function validSection(value: unknown): SportsSection {
  return ['football', 'volleyball', 'basketball', 'schedule'].includes(String(value))
    ? (value as SportsSection)
    : 'schedule'
}

const section = ref<SportsSection>(validSection(route.params.section))
const selectedSport = computed<SportSlug>(() =>
  section.value === 'schedule' ? admin.value.sport || 'football' : section.value,
)
const season = computed(() => seasons.value[selectedSport.value])

watch(
  () => route.params.section,
  value => (section.value = validSection(value)),
)

watch(section, value => {
  router.replace({ name: 'sports', params: { section: value } })
  refreshSection(value)
})

async function refreshSection(value: SportsSection) {
  try {
    if (value === 'schedule') {
      await sportsStore.updateSchedule(getISODate(getCurrentDate()))
    } else {
      await sportsStore.updateSport(value)
    }
  } catch (error) {
    displaySnackbar(
      error instanceof Error ? error.message : 'Športnih podatkov ni bilo mogoče naložiti',
    )
  }
}

async function logout() {
  try {
    await sportsStore.logout()
    displaySnackbar('Odjavljeni ste')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Odjava ni uspela')
  }
}

async function initialize() {
  try {
    await Promise.all([sportsStore.updateSeasonList(), sportsStore.restoreAdminSession()])
    await refreshSection(section.value)
  } catch (error) {
    displaySnackbar(
      error instanceof Error ? error.message : 'Športnih podatkov ni bilo mogoče naložiti',
    )
  }
}

initialize()
</script>

<template>
  <div class="sports-view">
    <v-tabs
      v-if="!mobile"
      v-model="section"
      center-active
      show-arrows
      class="mb-4"
      aria-label="Tekme"
    >
      <v-tab value="schedule" text="Tedenski razpored" />
      <v-tab value="football" text="Nogomet" />
      <v-tab value="volleyball" text="Odbojka" />
      <v-tab value="basketball" text="Košarka" />
    </v-tabs>

    <div v-if="admin.authenticated" class="d-flex justify-end mb-4">
      <div class="d-flex align-center ga-2">
        <v-chip :prepend-icon="mdiTrophy" color="secondary">
          Urejanje: {{ sportNames[admin.sport!] }}
        </v-chip>
        <v-btn :prepend-icon="mdiLogout" text="Odjava" variant="outlined" @click="logout" />
      </div>
    </div>

    <SportsSchedule v-if="section === 'schedule'" />
    <SportsTournament
      v-else-if="season"
      :sport="selectedSport"
      :season="season"
      :editable="sportsStore.canEdit(selectedSport)"
    />
    <v-progress-linear v-else indeterminate color="secondary" />
  </div>
</template>
