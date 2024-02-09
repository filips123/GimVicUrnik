<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  label: string
}>()

const emit = defineEmits(['update:modelValue'])

const isChecked = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})
</script>
<template>
  <v-list-item-switch :title="label">
    <template v-slot:append>
      <v-switch v-model="isChecked" style="grid-template-areas: none !important" />
    </template>
  </v-list-item-switch>
</template>
