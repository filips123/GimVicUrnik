<script setup lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { ref, watch } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import { sportNames, type SportSlug, useSportsStore } from '@/stores/sports'

const dialog = defineModel<boolean>()
const props = defineProps<{ initialSport?: SportSlug }>()

const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const sport = ref<SportSlug>(props.initialSport || 'football')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)

watch(
  () => props.initialSport,
  value => {
    if (value) sport.value = value
  },
)

async function login() {
  loading.value = true
  try {
    await sportsStore.login(sport.value, password.value)
    await sportsStore.updateSport(sport.value)
    password.value = ''
    dialog.value = false
    displaySnackbar(`Prijavljeni ste za urejanje: ${sportNames[sport.value]}`)
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Prijava ni uspela')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Prijava organizatorja">
      <template #text>
        <v-select
          v-model="sport"
          label="Šport"
          :items="[
            { title: 'Nogomet', value: 'football' },
            { title: 'Odbojka', value: 'volleyball' },
            { title: 'Košarka', value: 'basketball' },
          ]"
          class="mb-3"
        />
        <v-text-field
          v-model="password"
          label="Geslo"
          :append-inner-icon="showPassword ? mdiEye : mdiEyeOff"
          :type="showPassword ? 'text' : 'password'"
          autofocus
          @click:append-inner="showPassword = !showPassword"
          @keydown.enter="login"
        />
      </template>
      <template #actions>
        <v-btn text="Prekliči" @click="dialog = false" />
        <v-btn text="Prijava" :loading="loading" :disabled="!password" @click="login" />
      </template>
    </v-card>
  </v-dialog>
</template>
