<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'

import { useSnackbarStore } from '@/composables/snackbar'
import { useListsStore } from '@/stores/lists'
import { useSessionStore } from '@/stores/session'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { sortEntities } from '@/utils/entities'
import { localizeSelectEntityNotSelected, localizeSelectEntityTitle } from '@/utils/localization'

const entityTypeDialog = defineModel<boolean>()
const { welcome } = defineProps<{ welcome?: boolean }>()

const router = useRouter()
const { mobile, width } = useDisplay()

const sessionStore = useSessionStore()

const { classesList, teachersList, classroomsList } = storeToRefs(useListsStore())
const settingsStore = useListsStore()
const { updateLists } = settingsStore
updateLists()

const snackbarStore = useSnackbarStore()
const { displaySnackbar } = snackbarStore

const emptyClassrooms = ref(false)
const selectedEntities = ref([] as string[])
const entitiesDialog = ref(false)
const entityType = ref(EntityType.None)

const title = computed(() => localizeSelectEntityTitle(entityType.value))
const subtitle = computed(() => {
  if (selectedEntities.value.length) {
    return selectedEntities.value.join(', ')
  }
  return localizeSelectEntityNotSelected(entityType.value)
})

const entityList = computed(() => {
  switch (entityType.value) {
    case EntityType.Class:
      return classesList.value
    case EntityType.Teacher:
      return teachersList.value
    case EntityType.Classroom:
    case EntityType.EmptyClassrooms:
      return classroomsList.value
    default:
      return []
  }
})

watch(
  selectedEntities,
  () => (selectedEntities.value = sortEntities(entityType.value, selectedEntities.value)),
)

function displayNoneSelected() {
  switch (entityType.value) {
    case EntityType.Class:
      displaySnackbar('Izberite vsaj en razred')
      return
    case EntityType.Teacher:
      displaySnackbar('Izberite vsaj enega profesorja')
      return
    case EntityType.Classroom:
      displaySnackbar('Izberite vsaj eno učilnico')
      return
  }
}

function handleSelectEntityType(selectedEntity: EntityType) {
  selectedEntities.value = []
  entityType.value = selectedEntity
  emptyClassrooms.value = false
  entitiesDialog.value = true
  entityTypeDialog.value = false
}

function backToEntityTypeDialog() {
  entitiesDialog.value = false
  entityTypeDialog.value = true
}

watch(emptyClassrooms, () => {
  if (emptyClassrooms.value) {
    selectedEntities.value = ['Proste učilnice']
    entityType.value = EntityType.EmptyClassrooms
  } else {
    selectedEntities.value = []
    entityType.value = EntityType.Classroom
  }
})

function handleViewEntities() {
  if (selectedEntities.value.length) {
    entitiesDialog.value = false

    sessionStore.entityType = entityType.value
    sessionStore.entities = selectedEntities.value

    router.push({ name: 'timetable' })
  } else {
    displayNoneSelected()
  }
}

function handleSelectEntity() {
  if (selectedEntities.value.length) {
    entitiesDialog.value = false

    sessionStore.entityType = entityType.value
    sessionStore.entities = selectedEntities.value

    settingsStore.entityType = entityType.value
    settingsStore.entities = selectedEntities.value

    if (welcome) {
      router.push({ name: 'timetable' })
    }
  } else {
    displayNoneSelected()
  }
}
</script>

<template>
  <v-dialog v-model="entityTypeDialog" :persistent="welcome">
    <v-card title="izberite pogled">
      <template #text>
        <v-btn text="Razred" @click="handleSelectEntityType(EntityType.Class)" />
        <v-btn text="Profesor" @click="handleSelectEntityType(EntityType.Teacher)" />
        <v-btn text="Učilnica" @click="handleSelectEntityType(EntityType.Classroom)" />
      </template>
      <template v-if="!welcome" #actions>
        <v-btn text="Zapri" @click="entityTypeDialog = false" />
      </template>
    </v-card>
  </v-dialog>
  <v-dialog v-model="entitiesDialog" height="25rem" persistent>
    <v-card :title :subtitle>
      <v-checkbox
        v-if="entityType === EntityType.Classroom || entityType === EntityType.EmptyClassrooms"
        v-model="emptyClassrooms"
        label="Proste učilnice"
      />
      <v-card-text-selection>
        <v-checkbox
          v-for="entity in entityList"
          :key="entity"
          v-model="selectedEntities"
          :label="entity"
          :value="entity"
          :disabled="emptyClassrooms"
        />
      </v-card-text-selection>
      <template #actions>
        <v-btn
          v-if="width >= 270"
          text="Nazaj"
          :class="{ 'mobile-buttons': mobile }"
          @click="backToEntityTypeDialog()"
        />
        <template v-if="!welcome">
          <v-btn
            text="Zapri"
            :class="{ 'mobile-buttons': mobile }"
            @click="entitiesDialog = false"
          />
          <v-btn text="Oglej" :class="{ 'mobile-buttons': mobile }" @click="handleViewEntities()" />
        </template>
        <v-btn text="Shrani" :class="{ 'mobile-buttons': mobile }" @click="handleSelectEntity()" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
.mobile-buttons {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
