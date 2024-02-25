<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { SnackType, useSettingsStore } from '@/stores/settings'
import { localizeSnackType } from '@/utils/localization'

const dialog = defineModel<boolean>()

const { snackType } = storeToRefs(useSettingsStore())

const menus = Object.values(SnackType)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite malico">
      <v-card-text-selection>
        <v-radio-group v-model="snackType">
          <v-radio
            v-for="menu in menus"
            :key="menu"
            :label="localizeSnackType(menu)"
            :value="menu"
          />
        </v-radio-group>
      </v-card-text-selection>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
