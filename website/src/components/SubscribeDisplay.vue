<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ label: string; url: string; schema?: string }>()

const targetUrl = computed(() =>
  props.schema ? props.url.replace(/^https?/, props.schema) : props.url,
)

function copyLink() {
  navigator.clipboard.writeText(props.url)
}
</script>

<template>
  <h3 class="text-h6 pt-1">{{ label }}</h3>
  <v-text-field
    :value="url"
    :aria-label="label"
    readonly
    density="compact"
    @click="$event.target.select()"
  />
  <div class="pt-1 pb-2 d-print-none">
    <v-btn-subscribe text="Kopiraj" @click="copyLink()" />
    <v-btn-subscribe text="Odpri" :href="targetUrl" target="_blank" />
  </div>
</template>
