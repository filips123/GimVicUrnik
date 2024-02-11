<script setup lang="ts">
import { ThemeType, useSettingsStore } from '@/stores/settings'
import { localizeThemeType } from '@/utils/localization'
import { storeToRefs } from 'pinia'
import { watch } from 'vue'
import { useTheme } from 'vuetify'

const dialog = defineModel<boolean>()

const { themeType } = storeToRefs(useSettingsStore())
const theme = useTheme()

watch(themeType, () => {
  if (themeType.value === ThemeType.System) {
    theme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'darkTheme'
      : 'lightTheme'
    return
  }

  theme.global.name.value = themeType.value
})

const themes = Object.values(ThemeType)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite barvno temo">
      <v-card-text-selection>
        <v-radio-group v-model="themeType">
          <v-radio
            v-for="theme in themes"
            :key="theme"
            :label="localizeThemeType(theme)"
            :value="theme"
          />
        </v-radio-group>
      </v-card-text-selection>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
