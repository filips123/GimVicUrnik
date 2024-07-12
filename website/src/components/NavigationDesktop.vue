<script setup lang="ts">
import { mdiChevronLeft, mdiChevronRight } from '@mdi/js'
import { ref } from 'vue'

const { navigation } = defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()

const rail = ref(true)
</script>

<!-- TODO: Can we get back rounded buttons? -->

<template>
  <v-navigation-drawer :rail>
    <v-list class="pt-0" tabindex="-2">
      <v-list-item
        v-for="page in navigation"
        :key="page.link"
        :title="page.title"
        :aria-label="page.title"
        :prepend-icon="page.icon"
        :to="{ name: page.link }"
        tabindex="0"
      />
    </v-list>
    <template #append>
      <v-list-item
        :aria-label="rail ? 'Strni' : 'Razširi'"
        :prepend-icon="rail ? mdiChevronRight : mdiChevronLeft"
        role="button"
        @click="rail = !rail"
      />
    </template>
  </v-navigation-drawer>
</template>
