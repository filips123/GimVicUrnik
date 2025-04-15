<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { watch } from 'vue'

import { useNotificationsStore } from '@/stores/notifications'
import { SnackType, useSettingsStore } from '@/stores/settings'
import { localizeSnackType } from '@/utils/localization'

const dialog = defineModel<boolean>()

const { snackType } = storeToRefs(useSettingsStore())

const notificationsStore = useNotificationsStore()

watch(snackType, () => notificationsStore.updateUserFirestoreData())
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Izberite vrsto malice">
      <template #text>
        <v-radio-group v-model="snackType">
          <v-radio
            v-for="menu in Object.values(SnackType)"
            :key="menu"
            :label="localizeSnackType(menu)"
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
