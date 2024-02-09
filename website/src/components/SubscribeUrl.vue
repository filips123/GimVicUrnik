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
  <v-text-field readonly :value="url" :label="label" @click="$event.target.select()" />
  <div class="pb-3">
    <v-btn-subscribe @click="copyLink()" text="Kopiraj" />
    <v-btn-subscribe @click="openLink()" text="Odpri" />
  </div>
</template>
