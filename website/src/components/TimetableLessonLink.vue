<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSettingsStore } from '@/stores/settings'

defineProps<{
  linkType: string
  linkValue: string | null
}>()

const { showLinksInTimetable } = storeToRefs(useSettingsStore())
</script>

<template>
  <router-link
    v-if="showLinksInTimetable && linkValue"
    :to="{ name: 'timetable', params: { type: linkType, value: linkValue } }"
    class="text-decoration-none"
    >{{ linkValue }}</router-link
  >
  <template v-else-if="linkValue">{{ linkValue }}</template>
  <template v-else>/</template>
</template>
