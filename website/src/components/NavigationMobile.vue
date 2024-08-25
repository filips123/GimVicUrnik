<script setup lang="ts">
defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()
</script>

<template>
  <v-bottom-navigation grow role="navigation" aria-label="Navigacija" class="d-print-none">
    <v-btn
      v-for="page in navigation"
      :key="page.link"
      :text="page.title"
      :aria-label="page.title"
      :prepend-icon="page.icon"
      :to="{ name: page.link }"
    />
  </v-bottom-navigation>
</template>
