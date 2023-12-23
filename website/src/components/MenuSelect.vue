<script setup lang="ts">
import { ref, watch, computed } from 'vue'

import { SnackType, LunchType, MenuType, useSettingsStore } from '@/stores/settings'

import { localizeSnackTypeList, localizeLunchTypeList } from '@/composables/localization'

const props = defineProps<{
  modelValue: boolean
  menuType: MenuType
}>()

const emit = defineEmits(['update:modelValue'])

const menuSelectionDialog = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  }
})

const settingsStore = useSettingsStore()

const selectedMenuIndex = ref(0)

function getMenuList() {
  switch (props.menuType) {
    case MenuType.Snack:
      selectedMenuIndex.value = settingsStore.snackType
      return localizeSnackTypeList
    case MenuType.Lunch:
      selectedMenuIndex.value = settingsStore.lunchType
      return localizeLunchTypeList
  }
}

watch(selectedMenuIndex, (newMenuIndex: SnackType | LunchType) => {
  switch (props.menuType) {
    case MenuType.Snack:
      settingsStore.snackType = newMenuIndex as SnackType
      return
    case MenuType.Lunch:
      settingsStore.lunchType = newMenuIndex as LunchType
      return
  }
})
</script>

<template>
  <v-dialog v-model="menuSelectionDialog" scrollable width="25rem">
    <v-card>
      <v-card-title class="bg-green uppercase">IZBERITE MALICO</v-card-title>
      <v-card-text class="pa-0 h-300">
        <v-radio-group v-model="selectedMenuIndex" color="green">
          <v-radio
            v-for="(menu, indexMenu) in getMenuList()"
            :label="menu"
            :value="indexMenu"
            class="pl-1"></v-radio>
        </v-radio-group>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="green" @click="menuSelectionDialog = false">V redu</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
