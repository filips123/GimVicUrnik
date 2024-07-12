<script setup lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import { useSettingsStore } from '@/stores/settings'

const dialog = defineModel<boolean>()
const callback = defineModel<boolean>('callback', { default: undefined })

const { circularsPassword } = storeToRefs(useSettingsStore())
const { displaySnackbar } = useSnackbarStore()

const inputShow = ref(false)

function closeDialog() {
  dialog.value = false

  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    displaySnackbar('Geslo je pravilno')
    callback.value = true
  } else if (circularsPassword.value !== '') {
    displaySnackbar('Geslo je napačno')
    circularsPassword.value = ''
  }
}
</script>

<!-- TODO: Styling, etc -->

<template>
  <v-dialog v-model="dialog">
    <v-card title="Vpišite geslo">
      <template #text>
        <p>
          Za ogled okrožnic znotraj aplikacije je potrebno geslo. Geslo je dostopno na
          <a href="https://ucilnica.gimvic.org/" target="_blank">spletni učilnici</a>.
        </p>
        <v-text-field
          v-model="circularsPassword"
          label="Geslo"
          :append-icon="inputShow ? mdiEye : mdiEyeOff"
          :type="inputShow ? 'text' : 'password'"
          autofocus
          @click:append="inputShow = !inputShow"
          @keyup.enter="closeDialog()"
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="closeDialog()" />
      </template>
    </v-card>
  </v-dialog>
</template>
