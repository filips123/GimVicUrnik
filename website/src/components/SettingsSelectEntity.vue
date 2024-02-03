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
      return 'Izberite razred in izbirne predmete'
    case EntityType.Teacher:
      return 'Izberite profesorje'
    case EntityType.Classroom:
      return 'Izberite učilnice'
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
      displaySnackbar('Izberite vsaj en razred ali izbirni predmet')
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
</script>

<template>
  <v-dialog v-model="selectEntityType" width="25rem" persistent>
    <v-card>
      <v-card-title class="bg-green">IZBERITE POGLED</v-card-title>
      <v-card-text>
        <v-btn
          @click="handleSelectEntityType(EntityType.Class)"
          color="green"
          variant="text"
          text="Razred"
        />
        <v-btn
          @click="handleSelectEntityType(EntityType.Teacher)"
          color="green"
          variant="text"
          text="Profesor"
        />
        <v-btn
          @click="handleSelectEntityType(EntityType.Classroom)"
          color="green"
          variant="text"
          text="Učilnica"
        />
      </v-card-text>
      <v-card-actions v-if="!welcome" class="justify-end">
        <v-btn color="green" @click="selectEntityType = false" text="Zapri" />
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="selectEntity" scrollable width="25rem" height="20rem" persistent>
    <v-card>
      <v-card-title class="bg-green uppercase">{{ title }}</v-card-title>
      <v-btn
        v-if="entityType === EntityType.Classroom"
        @click="handleEmptyClassrooms()"
        class="text-left"
        color="green"
        variant="text"
        text="Proste učilnice"
      />
      <v-card-subtitle class="pa-2">
        Vaša izbira: {{ sortedSelectEntityList.join(', ') }}
      </v-card-subtitle>
      <v-card-text class="pa-0 h-300">
        <v-checkbox
          v-for="entity in sortedEntityList"
          v-model="selectEntityList"
          :label="entity.toString()"
          :value="entity"
          color="green"
          class="pl-1"
        />
      </v-card-text>
      <v-card-actions class="justify-end">
        <template v-if="!welcome">
          Shrani:
          <v-switch hide-details v-model="saveSelection" color="green" class="pl-2" />
          <v-btn
            color="green"
            :class="{ 'ma-0': mobile, 'pa-0': mobile }"
            :style="{ 'min-width': 0 + 'px' }"
            @click="selectEntity = false"
            text="Zapri"
          />
        </template>
        <v-btn
          color="green"
          :class="{ 'ma-0': mobile, 'pa-0': mobile }"
          @click="backToSelectEntityType()"
          text="Nazaj"
        />
        <v-btn
          color="green"
          :class="{ 'ma-0': mobile, 'pa-0': mobile }"
          @click="handleSelectEntity()"
          text="V redu"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style>
.v-checkbox > .v-input__details {
  display: none;
}

.v-input--density-default {
  --v-input-control-height: 0px !important;
}
</style>
