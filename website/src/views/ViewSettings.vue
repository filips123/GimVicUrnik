<script setup lang="ts">
import {
  mdiDatabaseImportOutline,
  mdiInformationOutline,
  mdiKeyOutline,
  mdiMessageAlertOutline,
  mdiPaletteOutline,
  mdiTuneVariant,
  mdiUpdate,
  mdiWeatherNight,
} from '@mdi/js'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import SettingsAbout from '@/components/SettingsAbout.vue'
import SettingsBaseAction from '@/components/SettingsBaseAction.vue'
import SettingsBaseSwitch from '@/components/SettingsBaseSwitch.vue'
import SettingsFeedback from '@/components/SettingsFeedback.vue'
import SettingsSelectAccentColor from '@/components/SettingsSelectAccentColor.vue'
import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'
import SettingsSelectMenuLunch from '@/components/SettingsSelectMenuLunch.vue'
import SettingsSelectMenuSnack from '@/components/SettingsSelectMenuSnack.vue'
import SettingsSelectTheme from '@/components/SettingsSelectTheme.vue'
import SettingsSetDataCollection from '@/components/SettingsSetDataCollection.vue'
import SettingsSetMoodleToken from '@/components/SettingsSetMoodleToken.vue'
import { useSettingsStore } from '@/stores/settings'
import {
  localizeAccentColorName,
  localizeDataCollection,
  localizeEntityLabel,
  localizeLunchType,
  localizeSnackType,
  localizeThemeType,
} from '@/utils/localization'
import { updateAllData } from '@/utils/update'

const {
  entityList,
  entityType,
  snackType,
  lunchType,
  showSubstitutions,
  showLinksInTimetable,
  showHoursInTimetable,
  highlightCurrentTime,
  enableLessonDetails,
  enablePullToRefresh,
  dataCollectionPerformance,
  dataCollectionCrashes,
  themeType,
  accentColor,
  moodleToken,
  dataVersion,
} = storeToRefs(useSettingsStore())

const selectEntityDialog = ref(false)
const selectSnackDialog = ref(false)
const selectLunchDialog = ref(false)
const selectThemeDialog = ref(false)
const selectAccentColorDialog = ref(false)
const setDataCollectionDialog = ref(false)
const setMoodleTokenDialog = ref(false)
const aboutDialog = ref(false)
const feedbackDialog = ref(false)

const appVersion = import.meta.env.VITE_VERSION

async function updateApp() {
  // Add GET parameter to invalidate the cache of the index HTML file
  // The service worker waiting is skipped on the next load
  location.href = '?update=' + new Date().getTime()
}
</script>

<template>
  <v-column>
    <SettingsBaseAction
      v-model="selectEntityDialog"
      :label="localizeEntityLabel(entityType)"
      :messages="entityList.join(', ') || 'Ni nastavljen'"
      :icon="mdiTuneVariant"
    />

    <SettingsBaseAction
      v-model="selectSnackDialog"
      label="Vrsta malice"
      :messages="localizeSnackType(snackType)"
      :icon="mdiTuneVariant"
    />

    <SettingsBaseAction
      v-model="selectLunchDialog"
      label="Vrsta kosila"
      :messages="localizeLunchType(lunchType)"
      :icon="mdiTuneVariant"
    />

    <v-divider-settings />

    <SettingsBaseSwitch v-model="showSubstitutions" label="Prikaži nadomeščanja" />
    <SettingsBaseSwitch v-model="showLinksInTimetable" label="Prikaži povezave v urniku" />
    <SettingsBaseSwitch v-model="showHoursInTimetable" label="Prikaži ure v urniku" />
    <SettingsBaseSwitch v-model="highlightCurrentTime" label="Označi trenutno uro" />
    <SettingsBaseSwitch v-model="enableLessonDetails" label="Klikni za podrobnosti" />
    <SettingsBaseSwitch v-model="enablePullToRefresh" label="Potegni za posodobitev" />

    <v-divider-settings />

    <SettingsBaseAction
      v-model="selectThemeDialog"
      label="Barvna tema"
      :messages="localizeThemeType(themeType)"
      :icon="mdiWeatherNight"
    />

    <SettingsBaseAction
      v-model="selectAccentColorDialog"
      label="Barva označevanja"
      :messages="localizeAccentColorName(accentColor)"
      :icon="mdiPaletteOutline"
    />

    <SettingsBaseAction
      v-model="setDataCollectionDialog"
      label="Zbiranje tehničnih podatkov"
      :messages="localizeDataCollection(dataCollectionPerformance, dataCollectionCrashes)"
      :icon="mdiDatabaseImportOutline"
    />

    <SettingsBaseAction
      v-model="setMoodleTokenDialog"
      label="Žeton za spletno učilnico"
      :messages="moodleToken ? 'Nastavljen' : 'Ni nastavljen'"
      :icon="mdiKeyOutline"
    />

    <v-divider-settings />

    <SettingsBaseAction
      label="Posodobi aplikacijo"
      :messages="`Trenutna različica: ${appVersion}`"
      :callback="updateApp"
      :icon="mdiUpdate"
    />

    <SettingsBaseAction
      label="Posodobi podatke"
      :messages="`Trenutna različica: ${dataVersion}`"
      :callback="updateAllData"
      :icon="mdiUpdate"
    />

    <v-divider-settings />

    <SettingsBaseAction
      v-model="aboutDialog"
      label="O aplikaciji"
      :messages="`Trenutna različica: ${appVersion}`"
      :icon="mdiInformationOutline"
    />

    <SettingsBaseAction
      v-model="feedbackDialog"
      label="Povratne informacije"
      :icon="mdiMessageAlertOutline"
    />

    <SettingsSelectEntity v-model="selectEntityDialog" />
    <SettingsSelectMenuSnack v-model="selectSnackDialog" />
    <SettingsSelectMenuLunch v-model="selectLunchDialog" />
    <SettingsSelectTheme v-model="selectThemeDialog" />
    <SettingsSelectAccentColor v-model="selectAccentColorDialog" />
    <SettingsSetDataCollection v-model="setDataCollectionDialog" />
    <SettingsSetMoodleToken v-model="setMoodleTokenDialog" />
    <SettingsAbout v-model="aboutDialog" />
    <SettingsFeedback v-model="feedbackDialog" />
  </v-column>
</template>
