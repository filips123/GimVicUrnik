<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import { useSettingsStore } from '@/stores/settings'

const dialog = defineModel<boolean>()

const { circularsPassword } = storeToRefs(useSettingsStore())
const snackbarStore = useSnackbarStore()
const { displaySnackbar } = snackbarStore

const inputShow = ref(false)

function closeDialog() {
  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    displaySnackbar('Geslo je pravilno')
  } else if (circularsPassword.value !== '') {
    displaySnackbar('Geslo je napačno')
    circularsPassword.value = ''
  }

  dialog.value = false
}
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Vpišite geslo">
      <template #text>
        <p>
          Za ogled okrožnic znotraj aplikacije je potrebno geslo. Geslo je dostopno na
          <a href="https://ucilnica.gimvic.org/">spletni učilnici</a>.
        </p>
        <v-divider />
        <v-text-field
          v-model="circularsPassword"
          label="Geslo"
          :append-icon="inputShow ? 'mdi-eye' : 'mdi-eye-off'"
          :type="inputShow ? 'text' : 'password'"
          @click:append="inputShow = !inputShow"
          @keyup.enter="closeDialog()"
          autofocus
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="closeDialog()" />
      </template>
    </v-card>
  </v-dialog>
</template>
