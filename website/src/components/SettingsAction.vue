<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  icon: string
  messages: string
  modelValue?: boolean
  label: string
}>()

const emit = defineEmits(['update:modelValue'])

const action = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})
</script>
<template>
  <v-input class="mb-6" :append-icon="icon" :messages="messages" @click="action = true">
    {{ label }}
  </v-input>
</template>
