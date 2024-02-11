<script setup lang="ts">
import { LunchType, useSettingsStore } from '@/stores/settings'
import { localizeLunchType } from '@/utils/localization'
import { storeToRefs } from 'pinia'

const dialog = defineModel<boolean>()

const { lunchType } = storeToRefs(useSettingsStore())

const menus = Object.values(LunchType)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite kosilo">
      <v-card-text-selection>
        <v-radio-group v-model="lunchType">
          <v-radio
            v-for="menu in menus"
            :key="menu"
            :label="localizeLunchType(menu)"
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
