<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useSnackbarStore } from '@/stores/snackbar'

const { show, message, buttonText, buttonAction, timeout } = storeToRefs(useSnackbarStore())
</script>

<template>
  <v-snackbar v-model="show" :timeout="timeout" :text="message">
    <template v-slot:actions v-if="buttonText">
      <v-btn @click="buttonAction">
        {{ buttonText }}
      </v-btn>
    </template>
  </v-snackbar>
</template>
