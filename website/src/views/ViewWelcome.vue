<script setup lang="ts">
import { ref, watch } from 'vue'

import SettingsSelectEntity from '@/components/SettingsSelectEntity.vue'
import WelcomeInformation from '@/components/WelcomeInformation.vue'
import { updateAllData } from '@/utils/update'

const welcomeDialog = ref(true)
const settingsDialog = ref(false)

// TODO: Display welcome wizard without dialogs
// TODO: Check if this can be on the root URL

watch(welcomeDialog, () => (settingsDialog.value = true))

updateAllData(false)
</script>

<template>
  <WelcomeInformation v-model="welcomeDialog" />
  <SettingsSelectEntity v-model="settingsDialog" welcome />
</template>
