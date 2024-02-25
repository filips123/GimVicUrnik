<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { EntityType, useSettingsStore } from '@/stores/settings'
import { useUserStore } from '@/stores/user'

const props = defineProps<{
  entityTypeLink: EntityType
  substitution: boolean
  originalEntity: string
  substitutionEntity: string
}>()

const { entityType, entities } = storeToRefs(useUserStore())

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
  ></td>
</template>
