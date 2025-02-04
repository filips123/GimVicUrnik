<script setup lang="ts">
const checked = defineModel<boolean>()
defineProps<{ label: string; messages?: string; icon?: string; disabled?: boolean }>()
</script>

<template>
  <v-row>
    <v-col>
      <v-switch
        v-model="checked"
        :disabled
        :label
        :messages
        :true-icon="icon"
        :false-icon="icon"
        class="settings-base-switch"
      />
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
