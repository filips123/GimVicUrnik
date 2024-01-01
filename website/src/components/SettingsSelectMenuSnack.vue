<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import { SnackType, useSettingsStore } from '@/stores/settings'

import { localizeSnackType } from '@/composables/localization'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])

const selectSnack = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { snackType } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="selectSnack" scrollable width="25rem">
    <v-card>
      <v-card-title class="bg-green"> IZBERITE MALICO </v-card-title>
      <v-card-text class="pa-0 h-300">
        <v-radio-group v-model="snackType" color="green">
          <v-radio
            v-for="snackTypeValue in Object.values(SnackType)"
            :label="localizeSnackType(snackTypeValue)"
            :value="snackTypeValue"
          />
        </v-radio-group>
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn color="green" @click="selectSnack = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
