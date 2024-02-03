<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'

import { useSettingsStore, EntityType } from '@/stores/settings'

import { updateAllData } from '@/composables/update'
import {
  localizeEntityType,
  localizeSnackType,
  localizeLunchType,
  localizeThemeType,
} from '@/composables/localization'

import SettingsAction from '@/components/SettingsAction.vue'
import SettingsSwitch from '@/components/SettingsSwitch.vue'

import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'
import SettingsSelectMenuSnack from '@/components/SettingsSelectMenuSnack.vue'
import SettingsSelectMenuLunch from '@/components/SettingsSelectMenuLunch.vue'

import SettingsSelectTheme from '@/components/SettingsSelectTheme.vue'
import SettingsSetMoodleToken from '@/components/SettingsSetMoodleToken.vue'
import SettingsSetDataCollection from '@/components/SettingsSetDataCollection.vue'

import SettingsAbout from '@/components/SettingsAbout.vue'

const {
  entities,
  entityType,
  snackType,
  lunchType,
  showSubstitutions,
  showLinksInTimetable,
  showHoursInTimetable,
  showCurrentTime,
  enableShowingDetails,
  enablePullToRefresh,
  enableUpdateOnLoad,
  themeType,
  moodleToken,
  dataCollection,
  dataVersion,
} = storeToRefs(useSettingsStore())

const selectEntity = ref(false)
const selectSnack = ref(false)
const selectLunch = ref(false)

const selectTheme = ref(false)
const setMoodleToken = ref(false)
const setDataCollection = ref(false)

const about = ref(false)

const selectEntityLabel = computed(
  () =>
    (entityType.value === EntityType.Classroom || entityType.value === EntityType.EmptyClassrooms
      ? 'Izbrana '
      : 'Izbran ') + localizeEntityType(entityType.value),
)
</script>

<template>
  <div class="px-4 pt-4 mx-auto" style="max-width: 35rem">
    <SettingsAction
      icon="mdi-tune-variant"
      :messages="entities.join(', ')"
      v-model="selectEntity"
      :label="selectEntityLabel"
    />

    <SettingsAction
      icon="mdi-tune-variant"
      :messages="localizeSnackType(snackType)"
      v-model="selectSnack"
      label="Izbrana malica"
    />

    <SettingsAction
      icon="mdi-tune-variant"
      :messages="localizeLunchType(lunchType)"
      v-model="selectLunch"
      label="Izbrano kosilo"
    />

    <v-divider class="mb-6" />

    <SettingsSwitch v-model="showSubstitutions" label="Prikaži nadomeščanja" />
    <SettingsSwitch v-model="showLinksInTimetable" label="Prikaži povezave v urniku" />
    <SettingsSwitch v-model="showHoursInTimetable" label="Prikaži ure v urniku" />
    <SettingsSwitch v-model="showCurrentTime" label="Prikaži trenutno uro" />
    <SettingsSwitch v-model="enableShowingDetails" label="Klikni za podrobnosti" />
    <SettingsSwitch v-model="enablePullToRefresh" label="Potegni za posodobitev" />
    <SettingsSwitch v-model="enableUpdateOnLoad" label="Samodejno posodabljanje" />

    <v-divider class="mb-6" />

    <SettingsAction
      icon="mdi-weather-night"
      :messages="localizeThemeType(themeType)"
      v-model="selectTheme"
      label="Izbrana barvna tema"
    />

    <SettingsAction
      icon="mdi-key"
      :messages="moodleToken ? 'Nastavljen' : 'Ni nastavljen'"
      v-model="setMoodleToken"
      label="Moodle žeton"
    />

    <SettingsAction
      icon="mdi-database-import-outline"
      :messages="dataCollection ? 'Vklopljeno' : 'Izklopljeno'"
      v-model="setDataCollection"
      label="Zbiranje tehničnih podatkov"
    />

    <v-divider class="mb-6" />

    <SettingsAction
      icon="mdi-update"
      messages="TODO VERZIJA"
      label="Posodobi aplikacijo"
      @click=""
    />

    <SettingsAction
      icon="mdi-update"
      :messages="`Trenutna različica: ${dataVersion}`"
      label="Posodobi podatke"
      @click="updateAllData()"
    />

    <v-divider class="mb-6" />

    <SettingsAction
      icon="mdi-information-outline"
      messages="TODO VERZIJA"
      v-model="about"
      label="O Aplikaciji"
    />

    <SettingsSelectEntity v-model="selectEntity" />
    <SettingsSelectMenuSnack v-model="selectSnack" />
    <SettingsSelectMenuLunch v-model="selectLunch" />
    <SettingsSelectTheme v-model="selectTheme" />
    <SettingsSetMoodleToken v-model="setMoodleToken" />
    <SettingsSetDataCollection v-model="setDataCollection" />
    <SettingsAbout v-model="about" />
  </div>
</template>
<style>
.v-selection-control--density-default {
  --v-input-control-height: 0px;
}
</style>
