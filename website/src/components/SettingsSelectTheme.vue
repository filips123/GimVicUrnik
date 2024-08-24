<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { ThemeType, useSettingsStore } from '@/stores/settings'
import { localizeThemeType } from '@/utils/localization'

const dialog = defineModel<boolean>()

const { themeType } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite barvno temo">
      <template #text>
        <v-radio-group v-model="themeType">
          <v-radio
            v-for="theme in Object.values(ThemeType)"
            :key="theme"
            :label="localizeThemeType(theme)"
            :value="theme"
          />
        </v-radio-group>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
