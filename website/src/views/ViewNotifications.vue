<script setup lang="ts">
import { mdiClockOutline } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { computed, ref, watch } from 'vue'

import NotificationsSetTime from '@/components/NotificationsSetTime.vue'
import SettingsBaseAction from '@/components/SettingsBaseAction.vue'
import SettingsBaseSwitch from '@/components/SettingsBaseSwitch.vue'
import { useNotificationsStore } from '@/stores/notifications'

const {
  substitutionsNotificationsImmediate,
  substitutionsNotificationsSetTime,
  substitutionsNotificationsCurrentDayTime,
  substitutionsNotificationsNextDayTime,
  circularsNotificationsEnabled,
  snackMenuNotificationsEnabled,
  lunchMenuNotificationsEnabled,
} = storeToRefs(useNotificationsStore())

const notificationsStore = useNotificationsStore()

const setCurrentDayTimeDialog = ref(false)
const setNextDayTimeDialog = ref(false)

const permissionGranted = ref(Notification.permission === 'granted')

const currentDayTimeMessage = computed(() => {
  if (substitutionsNotificationsCurrentDayTime.value) {
    return 'Pošlji za trenutni dan ob '.concat(substitutionsNotificationsCurrentDayTime.value)
  } else {
    return 'Ni nastavljeno'
  }
})

const nextDayTimeMessage = computed(() => {
  if (substitutionsNotificationsNextDayTime.value) {
    return 'Pošlji za naslednji dan ob '.concat(substitutionsNotificationsNextDayTime.value)
  } else {
    return 'Ni nastavljeno'
  }
})

watch(
  [
    substitutionsNotificationsImmediate,
    substitutionsNotificationsSetTime,
    substitutionsNotificationsCurrentDayTime,
    substitutionsNotificationsNextDayTime,
    circularsNotificationsEnabled,
    snackMenuNotificationsEnabled,
    lunchMenuNotificationsEnabled,
  ],
  () => notificationsStore.updateUserFirestoreData(),
)

function requestPermission() {
  Notification.requestPermission().then(permission => {
    permissionGranted.value = permission === 'granted'
  })
}
</script>

<template>
  <v-column>
    <div @click="!permissionGranted ? requestPermission() : null">
      <SettingsBaseSwitch
        v-model="substitutionsNotificationsImmediate"
        :disabled="!permissionGranted"
        label="Nadomeščanja"
        messages="Pošilji sporočilo, ko pride do nadomeščanja"
      />

      <SettingsBaseSwitch
        v-model="substitutionsNotificationsSetTime"
        :disabled="!permissionGranted"
        label="Povzetek nadomeščanj"
        messages="Pošlji sporočilo s povzetkom nadomeščanj ob določeni uri"
      />

      <SettingsBaseAction
        v-if="substitutionsNotificationsSetTime"
        v-model="setCurrentDayTimeDialog"
        :disabled="!permissionGranted"
        label="Trenutni dan"
        :messages="currentDayTimeMessage"
        :icon="mdiClockOutline"
      />

      <SettingsBaseAction
        v-if="substitutionsNotificationsSetTime"
        v-model="setNextDayTimeDialog"
        :disabled="!permissionGranted"
        label="Naslednji dan"
        :messages="nextDayTimeMessage"
        :icon="mdiClockOutline"
      />

      <v-divider-settings />

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

    <NotificationsSetTime
      v-model:dialog="setCurrentDayTimeDialog"
      v-model:time="substitutionsNotificationsCurrentDayTime"
      title="Izberite uro za trenutni dan"
    />
    <NotificationsSetTime
      v-model:dialog="setNextDayTimeDialog"
      v-model:time="substitutionsNotificationsNextDayTime"
      title="Izberite uro za naslednji dan"
    />
  </v-column>
</template>
