<script setup lang="ts">
import { watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useTheme } from 'vuetify'

import { ThemeType, useSettingsStore } from '@/stores/settings'

import { localizeThemeType } from '@/composables/localization'

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
watch(themeType, () => {
  if (themeType.value === ThemeType.System) {
    theme.global.name.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'darkTheme'
      : 'lightTheme'
    return
  }

  theme.global.name.value = themeType.value
})
</script>

<template>
  <v-dialog v-model="selectTheme">
    <v-card title="Izberite barvno temo">
      <v-card-text-selection>
        <v-radio-group v-model="themeType">
          <v-radio
            v-for="themeTypeValue in Object.values(ThemeType)"
            :label="localizeThemeType(themeTypeValue)"
            :value="themeTypeValue"
          />
        </v-radio-group>
      </v-card-text-selection>
      <v-card-actions>
        <v-btn @click="selectTheme = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
