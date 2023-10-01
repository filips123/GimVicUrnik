<script setup lang="ts">
const { navigation } = defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()
</script>

<template>
  <v-bottom-navigation fixed grow>
    <v-btn
      v-for="tab in navigation"
      :to="{ name: tab.link }"
      :aria-label="tab.title"
      :prepend-icon="tab.icon"
    >
      {{ tab.title }}
    </v-btn>
  </v-bottom-navigation>
</template>
