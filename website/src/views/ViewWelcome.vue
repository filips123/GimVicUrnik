<script setup lang="ts">
import { computed, ref } from 'vue'

import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'
import WelcomeInformation from '@/components/WelcomeInformation.vue'

const welcomeDialog = ref(true)

const settingsDialog = computed({
  get: () => !welcomeDialog.value,
  set: value => (welcomeDialog.value = !value),
})
</script>

<template>
  <WelcomeInformation v-model="welcomeDialog" />
  <SettingsSelectEntity v-model="settingsDialog" full-page />
</template>
