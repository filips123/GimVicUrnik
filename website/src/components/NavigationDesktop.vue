<script setup lang="ts">
import { ref } from 'vue'

const rail = ref(true)

const { navigation } = defineProps<{
  navigation: { title: string; link: string; icon: string }[]
}>()
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
      ></v-btn>
    </template>
  </v-navigation-drawer>
</template>

<style>
/* IGNORE FOR NOW (SCSS) */

/* Fix jumping icons caused by closing expanded navigation drawer */
.v-navigation-drawer--custom-mini-variant {
  .v-list-item {
    justify-content: unset !important;
  }
}
</style>
