<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { localizedWeekdays } from '@/utils/localization'
import { storeToRefs } from 'pinia'

const { day } = storeToRefs(useUserStore())
</script>

<template>
  <v-tabs v-model="day" center-active>
    <v-tab v-for="day in localizedWeekdays" :key="day" :text="day" />
  </v-tabs>
</template>
