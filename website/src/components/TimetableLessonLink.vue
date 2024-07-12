<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'

const props = defineProps<{
  entityTypeLink: EntityType
  substitution: boolean
  originalEntity: string
  substitutionEntity: string
}>()

const { entityType, entityList: entities } = storeToRefs(useSessionStore())

const settingsStore = useSettingsStore()
const { showLinksInTimetable, showSubstitutions } = settingsStore

const entity =
  showSubstitutions && props.substitution ? props.substitutionEntity : props.originalEntity

const showLink = showLinksInTimetable && entity !== '/'

function changeEntity() {
  entityType.value =
    props.entityTypeLink !== EntityType.EmptyClassrooms
      ? props.entityTypeLink
      : EntityType.Classroom
  entities.value = [entity]
}
</script>

<template>
  <td
    :class="{ 'text-primary-variant': showLink }"
    @click="showLink ? changeEntity() : null"
    v-text="entity"
  />
</template>
