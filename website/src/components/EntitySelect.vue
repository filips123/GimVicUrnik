<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

import { EntityType, useSettingsStore } from '@/stores/settings'
import { useTimetableStore } from '@/stores/timetable'

import { useUserStore } from '@/stores/user'

const props = defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])

const chooseEntitySelectionDialog = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  }
})

const router = useRouter()

const settingsStore = useSettingsStore()

const timetableStore = useTimetableStore()
const { classesList, teachersList, classroomsList } = timetableStore

const userStore = useUserStore()

const saveSelection = ref(true)

const entitySelectionList = ref([] as string[])
const entitySelectionDialog = ref(false)
const selectionEntityType = ref(EntityType.None)

const entityList = computed(() => {
  switch (selectionEntityType.value) {
    case EntityType.Class:
      return classesList
    case EntityType.Teacher:
      return teachersList
    case EntityType.Classroom:
      return classroomsList
  }

  return []
})

const sortedEntityList = computed(() =>
  entityList.value.sort((entity1, entity2) => {
    if (selectionEntityType.value != EntityType.Teacher) {
      if (entity1.length < entity2.length) {
        return -1
      } else if (entity1.length > entity2.length) {
        return 1
      }
    }

    return entity1 < entity2 ? -1 : 1
  })
)

function handleEntitySelection() {
  userStore.entityType = selectionEntityType.value
  userStore.entities = entitySelectionList.value

  if (saveSelection.value) {
    settingsStore.entityType = selectionEntityType.value
    settingsStore.entities = entitySelectionList.value
  } else {
    router.push({ name: 'timetable' })
  }

  entitySelectionList.value = []
  saveSelection.value = true
}

const title = computed(() => {
  switch (selectionEntityType.value) {
    case EntityType.Class:
      return 'Izberite razred in izbirne predmete'
    case EntityType.Teacher:
      return 'Izberite profesorje'
    case EntityType.Classroom:
      return 'Izberite učilnice'
  }
})
</script>

<template>
  <v-dialog v-model="chooseEntitySelectionDialog" width="25rem">
    <v-card>
      <v-card-title class="bg-green">IZBERITE POGLED</v-card-title>
      <v-card-text>
        <v-btn
          @click="
            selectionEntityType = EntityType.Class
            entitySelectionDialog = true
            chooseEntitySelectionDialog = false
          "
          color="green"
          variant="text"
          >Razred</v-btn
        >
        <v-btn
          @click="
            selectionEntityType = EntityType.Teacher
            entitySelectionDialog = true
            chooseEntitySelectionDialog = false
          "
          color="green"
          variant="text"
          >Profesor</v-btn
        >
        <v-btn
          @click="
            selectionEntityType = EntityType.Classroom
            entitySelectionDialog = true
            chooseEntitySelectionDialog = false
          "
          color="green"
          variant="text"
          >Učilnica</v-btn
        >
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="green" @click="chooseEntitySelectionDialog = false">Zapri</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="entitySelectionDialog" persistent scrollable width="25rem" height="25rem">
    <v-card>
      <v-card-title class="bg-green uppercase">{{ title }}</v-card-title>
      <v-card-subtitle class="pa-2"
        >Vaša izbira: {{ entitySelectionList.join(', ') }}</v-card-subtitle
      >
      <v-card-text class="pa-0 h-300">
        <v-checkbox
          v-for="entity in sortedEntityList"
          v-model="entitySelectionList"
          :label="entity.toString()"
          :value="entity"
          color="green"
          class="pl-1"></v-checkbox>
      </v-card-text>
      <v-card-actions class="pt-0">
        Shrani izbiro:
        <v-switch hide-details v-model="saveSelection" color="green" class="pl-2"></v-switch>
        <v-btn
          color="green"
          @click="
            entitySelectionDialog = false
            entitySelectionList = []
          "
          >Zapri</v-btn
        >
        <v-btn
          color="green"
          @click="
            entitySelectionDialog = false
            handleEntitySelection()
          "
          >V redu</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style>
.v-checkbox > .v-input__details {
  display: none;
}

.v-selection-control--density-default {
  --v-input-control-height: 0px;
}
</style>
