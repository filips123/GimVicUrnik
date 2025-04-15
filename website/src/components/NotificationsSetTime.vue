<script setup lang="ts">
import { ref } from 'vue'

const dialog = defineModel<boolean>('dialog')
const time = defineModel<string>('time')

defineProps<{ title: string }>()

const doPersist = ref(false) // Workaround for now

function turnOff() {
  time.value = ''
  dialog.value = false
}
</script>

<template>
  <v-dialog v-model="dialog" :persistent="doPersist">
    <v-card :title>
      <template #text>
        <v-time-picker
          v-model="time"
          :allowed-minutes="m => m % 15 === 0"
          scrollable
          format="24hr"
          header-color="primary"
          color="secondary"
          class="align-center mx-auto"
          @update:hour="doPersist = true"
          @update:model-value="doPersist = false"
        />
      </template>
      <template #actions>
        <v-btn text="Izklopi" @click="turnOff()" />
        <v-btn :disabled="doPersist" text="Shrani" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
.v-picker-title {
  display: none;
}
</style>
