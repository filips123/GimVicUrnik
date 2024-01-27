<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useSnackbarStore } from '@/stores/snackbar'

const { show, message, buttonText, buttonAction, timeout } = storeToRefs(useSnackbarStore())
</script>

<template>
  <v-snackbar
    v-model="show"
    :timeout="timeout"
    style="margin-bottom: 60px"
    width="300"
    min-width="auto"
  >
    {{ message }}
    <template v-slot:actions v-if="buttonText">
      <v-btn color="green" variant="text" @click="buttonAction">
        {{ buttonText }}
      </v-btn>
    </template>
  </v-snackbar>
</template>

<style>
.v-snackbar__content {
  text-align: center !important;
}
</style>
