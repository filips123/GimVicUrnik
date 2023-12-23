<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'

import { EntityType, MenuType, useSettingsStore } from '@/stores/settings'

import {
  localizeEntityType,
  localizeSnackType,
  localizeLunchType,
  localizeSwitchSettings
} from '@/composables/localization'

import EntitySelect from '@/components/EntitySelect.vue'
import MenuSelect from '@/components/MenuSelect.vue'
import ThemeSelect from '@/components/ThemeSelect.vue'
import SelectMoodleToken from '@/components/SelectMoodleToken.vue'
import SettingsAbout from '@/components/SettingsAbout.vue'

const settingsStore = useSettingsStore()

const {
  entityType,
  snackType,
  lunchType,
  showSubstitutions,
  showLinksInTimetable,
  showHoursInTimetable,
  showCurrentTime,
  enableShowingDetails,
  enablePullToRefresh,
  enableUpdateOnLoad
} = storeToRefs(useSettingsStore())

const switchModels = [
  showSubstitutions,
  showLinksInTimetable,
  showHoursInTimetable,
  showCurrentTime,
  enableShowingDetails,
  enablePullToRefresh,
  enableUpdateOnLoad
]

const entitySelect = ref(false)

const menuSelectionDialog = ref(false)

const menuType = ref(MenuType.Snack)
</script>

<template>
  <div class="settings px-4 pt-4">
    <v-input
      class="mb-6"
      append-icon="mdi-tune-variant"
      :messages="settingsStore.entities.join(', ')"
      @click="entitySelect = true">
      {{ entityType === EntityType.Classroom ? 'Izbrana' : 'Izbran' }}
      {{ localizeEntityType(entityType) }}
    </v-input>
    <v-input
      class="mb-6"
      append-icon="mdi-tune-variant"
      :messages="localizeSnackType(snackType)"
      @click="
        menuType = MenuType.Snack;
        menuSelectionDialog = true
      ">
      Izbrana malica
    </v-input>
    <v-input
      append-icon="mdi-tune-variant"
      :messages="localizeLunchType(lunchType)"
      @click="
        menuType = MenuType.Lunch;
        menuSelectionDialog = true
      ">
      Izbrano kosilo
    </v-input>

    <v-divider class="mt-6" />

    <entity-select v-model="entitySelect" />
    <menu-select v-model="menuSelectionDialog" :menuType="menuType" />

    <v-list>
      <v-list-item
        class="pa-0"
        v-for="(switchSettings, indexModel) in localizeSwitchSettings"
        :title="switchSettings">
        <template v-slot:append>
          <v-switch v-model="switchModels[indexModel].value" color="green"> </v-switch>
        </template>
      </v-list-item>
    </v-list>

    <v-divider class="my-6" />

    <!-- DATA collection -->
    <theme-select />
    <select-moodle-token />

    <v-divider class="my-6" />

    <!-- APP update -->
    LALA

    <v-divider class="my-6" />

    <settings-about />
  </div>
</template>

<style>
.settings {
  margin: 0 auto;
  max-width: 40rem;
}
</style>
