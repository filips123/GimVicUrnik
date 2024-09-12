<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, watch } from 'vue'
import { useTheme } from 'vuetify'

import { useSettingsStore } from '@/stores/settings'
import { ACCENT_COLORS } from '@/utils/colors'

const dialog = defineModel<boolean>()

const theme = useTheme()

const { accentColor } = storeToRefs(useSettingsStore())

const swatches = ACCENT_COLORS.map(({ primary }) => [primary])
const swatchesColor = ref(ACCENT_COLORS.find(color => color.name === accentColor.value)!.primary)

watch(
  swatchesColor,
  swatchesColor => {
    const color = ACCENT_COLORS.find(color => color.primary === swatchesColor)!

    accentColor.value = color.name

    theme.themes.value.light.colors.primary = color.primary
    theme.themes.value.light.colors.secondary = color.secondary
    theme.themes.value.light.variables['current-time-color'] = color.currentTime

    theme.themes.value.dark.colors.primary = color.primary
    theme.themes.value.dark.colors.secondary = color.secondary

    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', color.theme)
  },
  { immediate: true },
)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite barvo označevanja">
      <template #text>
        <v-color-picker
          v-model="swatchesColor"
          :swatches
          hide-canvas
          hide-sliders
          hide-inputs
          show-swatches
          elevation="0"
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
.v-color-picker-swatches > div {
  justify-content: left;
}
</style>
