<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSettingsStore } from '@/stores/settings'

const { linkType, linkValue } = defineProps<{
  linkType: string
  linkValue: string | null
}>()

const { showLinksInTimetable } = storeToRefs(useSettingsStore())
</script>

<template>
  <router-link
    v-if="showLinksInTimetable && linkValue"
    :to="{ name: 'timetable', params: { type: linkType, value: linkValue } }"
    class="text-primary-variant text-decoration-none"
    >{{ linkValue }}</router-link
  >
  <template v-else>{{ linkValue }}</template>
</template>
