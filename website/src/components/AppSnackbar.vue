<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSnackbarStore } from '@/composables/snackbar'

const { buttonAction, buttonText, show, text, timeout } = storeToRefs(useSnackbarStore())
</script>

<template>
  <v-snackbar v-model="show" :text :timeout color="surface-medium">
    <template v-if="buttonText" #actions>
      <v-btn :text="buttonText" color="secondary" @click="buttonAction" />
    </template>
  </v-snackbar>
</template>

<style>
/* Fix alignment with scrollbar and add animations */

.v-snackbar {
  padding-left: calc(var(--v-layout-left) + 100vw - 100%) !important;
  transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Make snackbar smaller by default */

.v-snackbar__wrapper {
  min-width: min(75%, 300px) !important;
  margin-bottom: 16px;
  margin-left: 8px;
  margin-right: 8px;
}
</style>
