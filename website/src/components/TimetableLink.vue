<script setup lang="ts">
import { computed } from 'vue'

import { useSettingsStore, EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

const props = defineProps<{
  entityType: EntityType
  substitution: boolean
  originalEntity: string
  substitutionEntity: string
}>()

const settingsStore = useSettingsStore()
const { entityType, entities } = storeToRefs(useUserStore())

const { showLinksInTimetable, showSubstitutions } = settingsStore

const entity = computed(() => {
  return showSubstitutions && props.substitution ? props.substitutionEntity : props.originalEntity
})

function changeEntity() {
  entityType.value = props.entityType
  entities.value = [entity.value]
}
</script>

<template>
  <td
    :class="{ 'text-blue': showLinksInTimetable }"
    @click="showLinksInTimetable ? changeEntity() : null"
  >
    {{ entity }}
  </td>
</template>
