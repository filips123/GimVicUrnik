<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'

import { useSettingsStore, EntityType } from '@/stores/settings'
import { useUserStore } from '@/stores/user'
import { useSnackbarStore } from '@/stores/snackbar'

import { sortEntityList } from '@/composables/entities'
import { storeToRefs } from 'pinia'

const props = defineProps<{
  modelValue: boolean
  welcome?: boolean
}>()
const emit = defineEmits(['update:modelValue'])

const selectEntityType = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const router = useRouter()
const { mobile } = useDisplay()

const userStore = useUserStore()
const settingsStore = useSettingsStore()

settingsStore.updateLists()
const { classesList, teachersList, classroomsList } = storeToRefs(useSettingsStore())

const snackbarStore = useSnackbarStore()
const { displaySnackbar } = snackbarStore

const saveSelection = ref(true)

const selectEntityList = ref([] as string[])
const selectEntity = ref(false)
const entityType = ref(EntityType.None)

function handleSelectEntityType(selectedEntity: EntityType) {
  selectEntityList.value = []
  entityType.value = selectedEntity
  selectEntity.value = true
  selectEntityType.value = false
}

const title = computed(() => {
  switch (entityType.value) {
    case EntityType.Class:
      return 'Izberite razred'
    case EntityType.Teacher:
      return 'Izberite profesorje'
    case EntityType.Classroom:
      return 'Izberite učilnice'
  }
})

const subtitle = computed(() => {
  if (selectEntityList.value.length) {
    return sortedSelectEntityList.value.join(', ')
  }

  switch (entityType.value) {
    case EntityType.Class:
      return 'Ni izbranega razreda'
    case EntityType.Teacher:
      return 'Ni izbranega profesorja'
    case EntityType.Classroom:
      return 'Ni izbrane učilnice'
  }
})

const entityList = computed(() => {
  switch (entityType.value) {
    case EntityType.Class:
      return classesList.value
    case EntityType.Teacher:
      return teachersList.value
    case EntityType.Classroom:
      return classroomsList.value
  }

  return []
})

const sortedEntityList = computed(() => sortEntityList(entityType.value, entityList.value))
const sortedSelectEntityList = computed(() =>
  sortEntityList(entityType.value, selectEntityList.value),
)

function handleSelectEntity() {
  if (selectEntityList.value.length) {
    selectEntity.value = false

    userStore.entityType = entityType.value
    userStore.entities = selectEntityList.value

    if (saveSelection.value) {
      settingsStore.entityType = entityType.value
      settingsStore.entities = selectEntityList.value
    } else {
      router.push({ name: 'timetable' })
    }

    saveSelection.value = true
    return
  }

  switch (entityType.value) {
    case EntityType.Class:
      displaySnackbar('Izberite vsaj en razred')
      return
    case EntityType.Teacher:
      displaySnackbar('Izberite vsaj enega profesorja')
      return
    case EntityType.Classroom:
      displaySnackbar('Izberite vsaj eno učilnico')
  }
}

function backToSelectEntityType() {
  selectEntity.value = false
  selectEntityType.value = true
}

function handleEmptyClassrooms() {
  selectEntity.value = false
  userStore.entityType = EntityType.EmptyClassrooms
  userStore.entities = ['Proste učilnice']

  if (saveSelection.value) {
    settingsStore.entityType = EntityType.EmptyClassrooms
    settingsStore.entities = ['Proste učilnice']
  } else {
    router.push({ name: 'timetable' })
  }

  saveSelection.value = true
}

function handleViewEntity() {
  saveSelection.value = false
  handleSelectEntity()
}
</script>

<template>
  <v-dialog v-model="selectEntityType">
    <v-card title="izberite pogled">
      <v-card-text class="justify-center">
        <v-btn @click="handleSelectEntityType(EntityType.Class)" text="Razred" />
        <v-btn @click="handleSelectEntityType(EntityType.Teacher)" text="Profesor" />
        <v-btn @click="handleSelectEntityType(EntityType.Classroom)" text="Učilnica" />
      </v-card-text>
      <v-card-actions v-if="!welcome">
        <v-btn @click="selectEntityType = false" text="Zapri" />
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="selectEntity" height="25rem" persistent>
    <v-card :title="title" :subtitle="subtitle">
      <v-btn
        v-if="entityType === EntityType.Classroom"
        @click="handleEmptyClassrooms()"
        text="Proste učilnice"
        class="bg-surface-variation"
      />
      <v-card-text-selection>
        <v-checkbox
          v-for="entity in sortedEntityList"
          v-model="selectEntityList"
          :label="entity.toString()"
          :value="entity"
        />
      </v-card-text-selection>
      <v-card-actions>
        <template v-if="!welcome">
          <v-btn
            :class="{ 'ma-0': mobile, 'pa-0': mobile }"
            @click="handleViewEntity"
            text="Oglej"
          />
          <v-btn
            :class="{ 'ma-0': mobile, 'pa-0': mobile }"
            @click="selectEntity = false"
            text="Zapri"
          />
        </template>
        <v-btn
          v-if="welcome"
          :class="{ 'ma-0': mobile, 'pa-0': mobile }"
          @click="backToSelectEntityType"
          text="Nazaj"
        />
        <v-btn
          :class="{ 'ma-0': mobile, 'pa-0': mobile }"
          @click="handleSelectEntity"
          text="Shrani"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
