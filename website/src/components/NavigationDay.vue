<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'

const { weekdays } = defineProps<{ weekdays: string[] }>()

const { day } = storeToRefs(useUserStore())
</script>

<template>
  <v-tabs v-model="day" center-active center>
    <v-tab v-for="day in weekdays">
      {{ day }}
    </v-tab>
  </v-tabs>
</template>

<style>
/* IGNORE FOR NOW (SCSS) */

/* Hide blank space before first tab on mobile */
.v-slide-group__prev {
  display: none !important;
}

@media (max-width: 600px) {
  .v-tab:nth-child(2) {
    margin-left: 0 !important;
  }
}

/* Change text color to white */
.v-tab--active {
  color: #fff !important;
}
</style>
