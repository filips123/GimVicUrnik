<script setup lang="ts">
import { ref } from 'vue'

const { navigation } = defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()

const rail = ref(true)
</script>

<template>
  <v-navigation-drawer :rail>
    <v-list>
      <v-list-item
        v-for="page in navigation"
        :key="page.title"
        :title="page.title"
        :aria-label="page.title"
        :prepend-icon="page.icon"
        :to="{ name: page.link }"
      />
    </v-list>
    <template #append>
      <v-btn-icon :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'" @click="rail = !rail" />
    </template>
  </v-navigation-drawer>
</template>
