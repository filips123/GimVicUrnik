<script setup lang="ts">
const checked = defineModel<boolean>()
defineProps<{ label: string }>()
</script>

<template>
  <v-row>
    <v-col>
      <v-switch v-model="checked" class="settings-base-switch">
        <template #label>{{ label }}</template>
      </v-switch>
    </v-col>
  </v-row>
</template>

<style>
/* Use consistent switch heights */

.settings-base-switch .v-selection-control {
  min-height: unset;
}

.settings-base-switch .v-selection-control__wrapper {
  height: 32px;
}
</style>
