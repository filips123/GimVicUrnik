<script setup lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import { useSettingsStore } from '@/stores/settings'

const dialog = defineModel<boolean>()
const callback = defineModel<boolean>('callback', { default: undefined })

defineProps<{ tip?: boolean }>()

const { circularsPassword } = storeToRefs(useSettingsStore())
const { displaySnackbar } = useSnackbarStore()

const inputShow = ref(false)

function closeDialog() {
  dialog.value = false

  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    callback.value = true
  } else if (circularsPassword.value !== '') {
    displaySnackbar('Geslo je napačno')
    circularsPassword.value = ''
  }
}
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Vpišite geslo">
      <template #text>
        <p class="pb-4 text-trim-end">
          Za ogled okrožnic je potrebno geslo. Dostopno je na
          <a href="https://ucilnica.gimvic.org/course/view.php?id=530" target="_blank"
            >spletni učilnici</a
          >.
        </p>
        <p v-if="tip" class="border-s-md border-info border-opacity-75 ps-3 py-0 mb-4">
          <strong>Nasvet:</strong> Če namesto na ikono ob okrožnici kliknete na njeno ime, se bo
          odprla znotraj aplikacije, brez da bi jo morali prenesti.
        </p>
        <v-text-field
          v-model="circularsPassword"
          label="Geslo"
          :append-inner-icon="inputShow ? mdiEye : mdiEyeOff"
          :type="inputShow ? 'text' : 'password'"
          @click:append-inner="inputShow = !inputShow"
          @keydown.enter="closeDialog()"
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="closeDialog()" />
      </template>
    </v-card>
  </v-dialog>
</template>
