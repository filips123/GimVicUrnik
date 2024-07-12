<script setup lang="ts">
const props = defineProps<{ label: string; url: string }>()

function copyLink() {
  navigator.clipboard.writeText(props.url)
}
</script>

<template>
  <v-text-field :label :value="url" readonly @click="$event.target.select()" />
  <div class="pb-3">
    <v-btn-subscribe text="Kopiraj" @click="copyLink()" />
    <v-btn-subscribe text="Odpri" :href="url" target="_blank" />
  </div>
</template>
