<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, watch } from 'vue'

import { useSettingsStore } from '@/stores/settings'
import { accentColors } from '@/utils/colors'

const dialog = defineModel<boolean>()

const swatches = accentColors.map(({ primary }) => [primary])

const { accentColor } = storeToRefs(useSettingsStore())
const selectedColor = ref(accentColors.find(color => color.name === accentColor.value)!.primary)

watch(
  selectedColor,
  selectedColor => {
    const color = accentColors.find(color => color.primary === selectedColor.toLowerCase())!
    accentColor.value = color.name
  },
  { immediate: true },
)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite barvo označevanja">
      <template #text>
        <v-color-picker
          v-model="selectedColor"
          class="align-center mx-auto"
          :swatches
          hide-canvas
          hide-sliders
          hide-inputs
          show-swatches
          elevation="0"
          width="min(100%, 350px)"
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
  padding-top: 10px !important;
  padding-bottom: 0 !important;
}
</style>
