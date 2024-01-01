<script setup lang="ts">
import { watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTheme } from 'vuetify'

import { ThemeType, useSettingsStore } from '@/stores/settings'

import { localizedThemeTypeList } from '@/composables/localization'

const props = defineProps<{ modelValue: boolean }>()

const emit = defineEmits(['update:modelValue'])

const selectTheme = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { themeType } = storeToRefs(useSettingsStore())
const theme = useTheme()

watch(themeType, (newThemeIndex: ThemeType) => {
  themeType.value = newThemeIndex as ThemeType
  // Yet to be implemented

  // switch (themeType.value) {
  //   case ThemeType.System:
  //     theme.global.name.value = 'system'
  //   case ThemeType.Light:
  //     theme.global.name.value = 'light'
  //   case ThemeType.Dark:
  //     theme.global.name.value = 'dark'
  // }
})
</script>

<template>
  <v-dialog v-model="selectTheme" scrollable width="25rem">
    <v-card>
      <v-card-title class="bg-green">IZBERITE BARVNO TEMO</v-card-title>
      <v-card-text class="pa-0 h-300">
        <v-radio-group v-model="themeType" color="green">
          <v-radio
            v-for="(theme, indexTheme) in localizedThemeTypeList"
            :label="theme"
            :value="indexTheme"
            class="pl-1"
          />
        </v-radio-group>
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn color="green" @click="selectTheme = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
