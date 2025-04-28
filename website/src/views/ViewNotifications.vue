<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref, watch } from 'vue'

import NotificationsList from '@/components/NotificationsList.vue'
import SettingsBaseSwitch from '@/components/SettingsBaseSwitch.vue'
import { useSnackbarStore } from '@/composables/snackbar'
import { useNotificationsStore } from '@/stores/notifications'

const {
  circularsNotificationsEnabled,
  snackMenuNotificationsEnabled,
  lunchMenuNotificationsEnabled,
  seen,
} = storeToRefs(useNotificationsStore())

const notificationsStore = useNotificationsStore()
const snackbarStore = useSnackbarStore()

const permissionGranted = ref(Notification.permission === 'granted')

watch(
  [circularsNotificationsEnabled, snackMenuNotificationsEnabled, lunchMenuNotificationsEnabled],
  () => notificationsStore.updateUserFirestoreData(),
)

function requestPermission() {
  Notification.requestPermission().then(permission => {
    permissionGranted.value = permission === 'granted'
    if (permissionGranted.value) notificationsStore.getFCMToken()
  })
}

if (!seen.value) {
  snackbarStore.$reset()
  seen.value = true
}
</script>

<template>
  <v-column>
    <div @click="!permissionGranted ? requestPermission() : null">
      <SettingsBaseSwitch
        v-model="circularsNotificationsEnabled"
        :disabled="!permissionGranted"
        label="Okrožnice"
        messages="Pošlji sporočilo, ko je na voljo nova okrožnica"
      />

      <v-divider-settings />

      <SettingsBaseSwitch
        v-model="snackMenuNotificationsEnabled"
        :disabled="!permissionGranted"
        label="Jedilnik malice"
        messages="Pošlji sporočilo, ko je na voljo jedilnik malice"
      />

      <SettingsBaseSwitch
        v-model="lunchMenuNotificationsEnabled"
        :disabled="!permissionGranted"
        label="Jedilnik kosila"
        messages="Pošlji sporočilo, ko je na voljo jedilnik kosila"
      />
    </div>

    <v-divider-settings />

    <NotificationsList />
  </v-column>
</template>
