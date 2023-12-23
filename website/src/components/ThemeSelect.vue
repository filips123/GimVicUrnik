<script setup lang="ts">
import { ref, watch } from 'vue'
import { useTheme } from 'vuetify'

import { ThemeType, useSettingsStore } from '@/stores/settings'

import { localizeThemeType, localizeThemeTypeList } from '@/composables/localization'

// Not working yet

const settingsStore = useSettingsStore()
const theme = useTheme()

const themeSelectionDialog = ref(false)
const selectedThemeIndex = ref(settingsStore.themeType)

watch(selectedThemeIndex, (newThemeIndex: ThemeType) => {
  settingsStore.themeType = newThemeIndex as ThemeType
  switch (settingsStore.themeType) {
    case ThemeType.System:
      theme.global.name.value = 'system'
    case ThemeType.Light:
      theme.global.name.value = 'light'
    case ThemeType.Dark:
      theme.global.name.value = 'dark'
  }
})
</script>

<template>
  <v-input
    class="my-6"
    append-icon="mdi-weather-night"
    :messages="localizeThemeType(settingsStore.themeType)"
    @click="themeSelectionDialog = true">
    Izbrana barvna tema
  </v-input>

  <v-dialog v-model="themeSelectionDialog" scrollable width="25rem">
    <v-card>
      <v-card-title class="bg-green uppercase">IZBERITE BARVNO TEMO</v-card-title>
      <v-card-text class="pa-0 h-300">
        <v-radio-group v-model="selectedThemeIndex" color="green">
          <v-radio
            v-for="(theme, indexTheme) in localizeThemeTypeList"
            :label="theme"
            :value="indexTheme"
            class="pl-1"></v-radio>
        </v-radio-group>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="green" @click="themeSelectionDialog = false">V redu</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
