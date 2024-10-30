<script setup lang="ts">
const model = defineModel<boolean>()

const { callback } = defineProps<{
  icon: string
  messages?: string
  label: string
  callback?: () => void
}>()

function doAction() {
  if (callback) return callback()
  model.value = true
}
</script>

<template>
  <v-row>
    <v-col>
      <v-input
        :messages
        :append-icon="icon"
        class="settings-base-action"
        tabindex="0"
        @click="doAction()"
        @keydown.enter="doAction()"
      >
        {{ label }}
      </v-input>
    </v-col>
  </v-row>
</template>

<style>
/* Make text unselectable and set pointer cursor */

.settings-base-action {
  cursor: pointer;
  user-select: none;
}

/* Align the icon to the center */

.settings-base-action .v-input__append {
  grid-row-start: 1;
  grid-row-end: 3;
  margin: auto 6px;
}

/* Style the element outline */

.settings-base-action {
  outline: 2px solid transparent;
  outline-offset: 4px;
  border-radius: 4px;
  transition: outline-color 0.2s ease-in-out;
}

.settings-base-action:focus-visible {
  outline-color: rgba(var(--v-theme-secondary), calc(0.25 * var(--v-theme-overlay-multiplier)));
}
</style>
