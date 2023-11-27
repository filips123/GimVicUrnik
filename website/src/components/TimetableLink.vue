<script setup lang="ts">
import { computed } from 'vue'

import { useSettingsStore, EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

const { entityType, substitution, originalEntity, substitutionEntity } = defineProps<{
  entityType: EntityType
  substitution: boolean
  originalEntity: string
  substitutionEntity: string
}>()

const userStore = useUserStore()
const settingsStore = useSettingsStore()

const { showLinksInTimetable, showSubstitutions } = settingsStore

const entity = computed(() => {
  return showSubstitutions && substitution ? substitutionEntity : originalEntity
})
</script>

<template>
  <td
    class="px-2"
    :class="{ 'text-blue': showLinksInTimetable }"
    @click="showLinksInTimetable ? userStore.changeEntity(entityType, entity) : null"
  >
    {{ entity }}
  </td>
</template>
