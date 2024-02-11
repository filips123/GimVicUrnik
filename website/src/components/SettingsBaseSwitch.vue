<script setup lang="ts">
const isChecked = defineModel<boolean>()
const { title } = defineProps<{ title: string }>()
</script>

<template>
  <v-list-item-switch :title>
    <template #append>
      <v-switch v-model="isChecked" style="grid-template-areas: none !important" />
    </template>
  </v-list-item-switch>
</template>
