<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'

import { useSettingsStore, LunchType } from '@/stores/settings'

import { localizeLunchType } from '@/composables/localization'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])

const selectLunch = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { lunchType } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="selectLunch">
    <v-card title="Izberite kosilo">
      <v-card-text-selection>
        <v-radio-group v-model="lunchType">
          <v-radio
            v-for="lunchTypeValue in Object.values(LunchType)"
            :label="localizeLunchType(lunchTypeValue)"
            :value="lunchTypeValue"
          />
        </v-radio-group>
      </v-card-text-selection>
      <v-card-actions>
        <v-btn @click="selectLunch = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
