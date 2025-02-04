<script setup lang="ts">
import { useEventListener } from '@vueuse/core'
import { storeToRefs } from 'pinia'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { useSnackbarStore } from '@/composables/snackbar'
import { useListsStore } from '@/stores/lists'
import { useNotificationsStore } from '@/stores/notifications'
import { EntityType, useSettingsStore } from '@/stores/settings'
import { sortEntities } from '@/utils/entities'
import { localizeSelectEntityNotSelected, localizeSelectEntityTitle } from '@/utils/localization'
import { generateTimetableRoute } from '@/utils/router'

const displayed = defineModel<boolean>()
const { fullPage } = defineProps<{ fullPage?: boolean }>()

const router = useRouter()

const notificationsStore = useNotificationsStore()

const settingsStore = useSettingsStore()
const { displaySnackbar } = useSnackbarStore()

const listsStore = useListsStore()
const { classesList, teachersList, classroomsList } = storeToRefs(listsStore)
const { updateLists } = listsStore

updateLists()

const entityTypeDialog = ref(false)
const entityListDialog = ref(false)

const selectedType = ref(EntityType.None)
const selectedList = ref([] as string[])
const selectedEmptyClassrooms = ref(false)

// Ensure the entity list is always sorted correctly
watch(
  selectedList,
  () => (selectedList.value = sortEntities(selectedType.value, selectedList.value)),
)

// Ensure the empty classrooms option is selected properly
watch(selectedEmptyClassrooms, selected => {
  if (selected) {
    selectedType.value = EntityType.EmptyClassrooms
    selectedList.value = ['Proste učilnice']
  } else {
    selectedType.value = EntityType.Classroom
    selectedList.value = []
  }
})

const title = computed(() => localizeSelectEntityTitle(selectedType.value))
const subtitle = computed(() =>
  selectedList.value.length
    ? selectedList.value.join(', ')
    : localizeSelectEntityNotSelected(selectedType.value),
)

const availableList = computed(() => {
  switch (selectedType.value) {
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

// Display the correct dialogs based on state
useEventListener(window, 'popstate', event => {
  if (event.state?.entityTypeDialog || event.state?.entityListDialog) {
    entityTypeDialog.value = event.state.entityTypeDialog
    entityListDialog.value = event.state.entityListDialog
  }
})

// Replace the history state with the initial state
onMounted(() => {
  history.replaceState(
    {
      ...history.state,
      entityTypeDialog: entityTypeDialog.value,
      entityListDialog: entityListDialog.value,
    },
    '',
  )
})

function pushState(entityTypeDialog: boolean, entityListDialog: boolean) {
  history.pushState(
    {
      ...history.state,
      position: history.state.position + 1,
      replaced: false,
      scroll: null,
      entityTypeDialog,
      entityListDialog,
    },
    '',
  )
}

watch(displayed, value => {
  if (value) {
    // Show the type selection dialog
    entityTypeDialog.value = true
    entityListDialog.value = false

    // Push a new history state where the type dialog is displayed
    pushState(true, false)
  }

  if (!value) {
    // Close all dialogs
    entityTypeDialog.value = false
    entityListDialog.value = false

    // Replace the history state with the closed state
    history.replaceState(
      {
        ...history.state,
        entityTypeDialog: false,
        entityListDialog: false,
      },
      '',
    )

    // Ensure the history stack is consistent
    pushState(false, false)
    history.back()
  }
})

watch([entityTypeDialog, entityListDialog], ([entityTypeValue, entityListValue]) => {
  if (!entityTypeValue && !entityListValue) {
    // Deactivate the component when both dialogs are closed
    displayed.value = false
  }
})

function navigateBack() {
  history.back()
}

function displayNoneSelected() {
  switch (selectedType.value) {
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
  // Prepare the inputs before showing the dialog
  selectedType.value = selectedEntity
  selectedList.value = []
  selectedEmptyClassrooms.value = false

  // Show the list selection dialog
  entityTypeDialog.value = false
  entityListDialog.value = true

  // Push a new history state where the list dialog is displayed
  pushState(false, true)
}

function handleViewEntityList() {
  if (!selectedList.value.length) {
    displayNoneSelected()
    return
  }

  // Navigate to the correct timetable route
  router.push(generateTimetableRoute(selectedType.value, selectedList.value))
}

function handleSaveEntityList() {
  if (!selectedList.value.length) {
    displayNoneSelected()
    return
  }

  // Store the chosen entity in the settings
  settingsStore.entityType = selectedType.value
  settingsStore.entityList = selectedList.value

  // Navigate to the correct timetable route or close the dialog
  if (fullPage) router.push(generateTimetableRoute(selectedType.value, selectedList.value))
  else displayed.value = false

  notificationsStore.updateUserFirestoreData()
}
</script>

<template>
  <v-dialog v-model="entityTypeDialog" :persistent="fullPage">
    <v-card title="Izberite pogled">
      <template #text>
        <div class="text-center">
          <v-btn text="Razred" @click="handleSelectEntityType(EntityType.Class)" />
          <v-btn text="Profesor" @click="handleSelectEntityType(EntityType.Teacher)" />
          <v-btn text="Učilnica" @click="handleSelectEntityType(EntityType.Classroom)" />
        </div>
      </template>
      <template v-if="!fullPage" #actions>
        <v-btn text="Zapri" @click="entityTypeDialog = false" />
      </template>
    </v-card>
  </v-dialog>

  <v-dialog v-model="entityListDialog" height="40rem" persistent>
    <v-card :title :subtitle>
      <template #text>
        <v-checkbox
          v-if="
            selectedType === EntityType.Classroom || selectedType === EntityType.EmptyClassrooms
          "
          v-model="selectedEmptyClassrooms"
          label="Proste učilnice"
        />
        <v-checkbox
          v-for="entity in availableList"
          :key="entity"
          v-model="selectedList"
          :label="entity"
          :value="entity"
          :disabled="selectedEmptyClassrooms"
        />
      </template>
      <template #actions>
        <v-btn text="Nazaj" @click="navigateBack()" />
        <template v-if="!fullPage">
          <v-btn text="Zapri" @click="entityListDialog = false" />
          <v-btn text="Poglej" @click="handleViewEntityList()" />
        </template>
        <v-btn text="Shrani" @click="handleSaveEntityList()" />
      </template>
    </v-card>
  </v-dialog>
</template>
