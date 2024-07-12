<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import SettingsAbout from '@/components/SettingsAbout.vue'
import SettingsBaseAction from '@/components/SettingsBaseAction.vue'
import SettingsBaseSwitch from '@/components/SettingsBaseSwitch.vue'
import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'
import SettingsSelectMenuLunch from '@/components/SettingsSelectMenuLunch.vue'
import SettingsSelectMenuSnack from '@/components/SettingsSelectMenuSnack.vue'
import SettingsSelectTheme from '@/components/SettingsSelectTheme.vue'
import SettingsSetDataCollection from '@/components/SettingsSetDataCollection.vue'
import SettingsSetMoodleToken from '@/components/SettingsSetMoodleToken.vue'
import { useSettingsStore } from '@/stores/settings'
import {
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
  showCurrentTime,
  enableLessonDetails,
  enablePullToRefresh,
  themeType,
  moodleToken,
} = storeToRefs(useSettingsStore())

const selectEntity = ref(false)
const selectSnack = ref(false)
const selectLunch = ref(false)
const selectTheme = ref(false)
const setMoodleToken = ref(false)
const setDataCollection = ref(false)
const about = ref(false)

function updateApp() {
  return // TODO
}
</script>

<template>
  <v-column>
    <SettingsBaseAction
      v-model="selectEntity"
      :label="localizeEntityLabel(entityType)"
      :messages="entityList.join(', ')"
      icon="mdi-tune-variant"
    />

    <SettingsBaseAction
      v-model="selectSnack"
      label="Izbrana malica"
      :messages="localizeSnackType(snackType)"
      icon="mdi-tune-variant"
    />

    <SettingsBaseAction
      v-model="selectLunch"
      label="Izbrano kosilo"
      :messages="localizeLunchType(lunchType)"
      icon="mdi-tune-variant"
    />

    <v-divider-settings />

    <SettingsBaseSwitch v-model="showSubstitutions" title="Prikaži nadomeščanja" />
    <SettingsBaseSwitch v-model="showLinksInTimetable" title="Prikaži povezave v urniku" />
    <SettingsBaseSwitch v-model="showHoursInTimetable" title="Prikaži ure v urniku" />
    <SettingsBaseSwitch v-model="showCurrentTime" title="Prikaži trenutno uro" />
    <SettingsBaseSwitch v-model="enableLessonDetails" title="Klikni za podrobnosti" />
    <SettingsBaseSwitch v-model="enablePullToRefresh" title="Potegni za posodobitev" />

    <v-divider-settings />

    <SettingsBaseAction
      v-model="selectTheme"
      label="Izbrana barvna tema"
      :messages="localizeThemeType(themeType)"
      icon="mdi-weather-night"
    />

    <SettingsBaseAction
      v-model="setMoodleToken"
      label="Moodle žeton"
      :messages="moodleToken ? 'Nastavljen' : 'Ni nastavljen'"
      icon="mdi-key"
    />

    <SettingsBaseAction
      v-model="setDataCollection"
      label="Zbiranje tehničnih podatkov"
      :messages="dataCollection ? 'Vklopljeno' : 'Izklopljeno'"
      icon="mdi-database-import-outline"
    />

    <v-divider-settings />

    <SettingsBaseAction
      label="Posodobi aplikacijo"
      messages="TODO VERZIJA"
      icon="mdi-update"
      @click="updateApp()"
    />

    <SettingsBaseAction
      label="Posodobi podatke"
      :messages="dataVersion"
      icon="mdi-update"
      @click="updateAllData()"
    />

    <v-divider-settings />

    <SettingsBaseAction
      v-model="about"
      label="O Aplikaciji"
      messages="TODO VERZIJA"
      icon="mdi-information-outline"
    />

    <SettingsSelectEntity v-model="selectEntity" />
    <SettingsSelectMenuSnack v-model="selectSnack" />
    <SettingsSelectMenuLunch v-model="selectLunch" />
    <SettingsSelectTheme v-model="selectTheme" />
    <SettingsSetMoodleToken v-model="setMoodleToken" />
    <SettingsSetDataCollection v-model="setDataCollection" />
    <SettingsAbout v-model="about" />
  </v-column>
</template>
