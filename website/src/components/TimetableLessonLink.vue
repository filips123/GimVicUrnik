<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed } from 'vue'

import { useSettingsStore } from '@/stores/settings'

const link = defineProps<{
  linkType: string
  isSubstitution: boolean
  originalEntity: string
  substitutionEntity: string
}>()

const { showLinksInTimetable, showSubstitutions } = storeToRefs(useSettingsStore())

const entityName = computed(() =>
  showSubstitutions.value && link.isSubstitution ? link.substitutionEntity : link.originalEntity,
)
</script>

<template>
  <td>
    <router-link
      v-if="showLinksInTimetable && entityName !== '/'"
      :to="{ name: 'timetable', params: { type: link.linkType, value: entityName } }"
      class="text-primary-variant text-decoration-none"
      >{{ entityName }}</router-link
    >
    <span v-else>{{ entityName }}</span>
  </td>
</template>
