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
  <v-list-item class="pa-0 mb-6" :title="label">
    <template v-slot:append>
      <v-switch v-model="isChecked" color="green" />
    </template>
  </v-list-item>
</template>

<style scoped>
.v-switch.v-input--horizontal {
  grid-template-areas: none;
}
</style>
