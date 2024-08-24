<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSnackbarStore } from '@/composables/snackbar'

const { buttonAction, buttonText, show, text, timeout } = storeToRefs(useSnackbarStore())
</script>

<template>
  <v-snackbar v-model="show" :text :timeout>
    <template v-if="buttonText" #actions>
      <v-btn :text="buttonText" @click="buttonAction" />
    </template>
  </v-snackbar>
</template>

<style>
.v-snackbar__wrapper {
  min-width: 250px !important;
  background-color: rgb(var(--v-theme-surface-variation-secundary)) !important;
}

.v-snackbar__content {
  text-align: center !important;
  color: rgb(var(--v-theme-text)) !important;
}

.v-snackbar__actions {
  color: rgb(var(--v-theme-primary)) !important;
}
</style>
