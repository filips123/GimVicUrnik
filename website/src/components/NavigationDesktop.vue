<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()

const rail = ref(true)
</script>

<template>
  <v-navigation-drawer :rail="rail">
    <v-list>
      <v-list-item
        v-for="tab in navigation"
        :to="{ name: tab.link }"
        :aria-label="tab.title"
        :prepend-icon="tab.icon"
        :title="tab.title"
        :value="tab.title"
      />
    </v-list>
    <template v-slot:append>
      <v-btn
        variant="text"
        :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
        @click.stop="rail = !rail"
      />
    </template>
  </v-navigation-drawer>
</template>
