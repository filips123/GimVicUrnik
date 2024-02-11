<script setup lang="ts">
const action = defineModel<boolean>()
const { icon, messages, label } = defineProps<{ icon: string; messages: string; label: string }>()
</script>

<template>
  <v-input :messages :append-icon="icon" class="mb-6" @click="action = true">
    {{ label }}
  </v-input>
</template>
