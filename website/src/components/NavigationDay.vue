<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

import { localizedWeekdays } from '@/composables/localization'

const { day } = storeToRefs(useUserStore())
</script>

<template>
  <v-tabs v-model="day" center-active>
    <v-tab v-for="day in localizedWeekdays">{{ day }}</v-tab>
  </v-tabs>
</template>
