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
  <v-dialog v-model="selectSnack">
    <v-card title="Izberite malico">
      <v-card-text-selection>
        <v-radio-group v-model="snackType">
          <v-radio
            v-for="snackTypeValue in Object.values(SnackType)"
            :label="localizeSnackType(snackTypeValue)"
            :value="snackTypeValue"
          />
        </v-radio-group>
      </v-card-text-selection>
      <v-card-actions>
        <v-btn @click="selectSnack = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
