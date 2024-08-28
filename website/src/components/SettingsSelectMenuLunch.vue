<script setup lang="ts">
import { storeToRefs } from 'pinia'

import { LunchType, useSettingsStore } from '@/stores/settings'
import { localizeLunchType } from '@/utils/localization'

const dialog = defineModel<boolean>()

const { lunchType } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite vrsto kosila">
      <template #text>
        <v-radio-group v-model="lunchType">
          <v-radio
            v-for="menu in Object.values(LunchType)"
            :key="menu"
            :label="localizeLunchType(menu)"
            :value="menu"
          />
        </v-radio-group>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
