<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSessionStore } from '@/stores/session'
import { localizedWeekdays } from '@/utils/localization'

const { day } = storeToRefs(useSessionStore())
</script>

<template>
  <v-tabs v-model="day" center-active role="tablist">
    <v-tab v-for="weekday in localizedWeekdays" :key="weekday" :text="weekday" />
  </v-tabs>
</template>
