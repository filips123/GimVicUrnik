<script setup lang="ts">
const props = defineProps<{ label: string; url: string }>()

function copyLink() {
  navigator.clipboard.writeText(props.url)
}

function openLink() {
  window.open(props.url, '_blank')
}
</script>

<template>
  <v-text-field :label :value="url" @click="$event.target.select()" readonly />
  <div class="pb-3">
    <v-btn-subscribe text="Kopiraj" @click="copyLink()" />
    <v-btn-subscribe text="Odpri" @click="openLink()" />
  </div>
</template>
