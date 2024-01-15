<script setup lang="ts">
const props = defineProps<{
  label: string
  url: string
}>()

function copyLink() {
  navigator.clipboard.writeText(props.url)
}

function openLink() {
  window.open(props.url, '_blank')
}
</script>

<template>
  <v-row class="pt-2">
    <h3>{{ label }}</h3>
  </v-row>

  <v-row>
    <v-text-field color="green" :value="url" @click="$event.target.select()" />
    <div class="pt-3">
      <v-btn variant="text" color="green" class="mx-1" @click="copyLink()" text="Kopiraj" />
      <v-btn variant="text" color="green" class="mx-1" @click="openLink()" text="Odpri" />
    </div>
  </v-row>
</template>
