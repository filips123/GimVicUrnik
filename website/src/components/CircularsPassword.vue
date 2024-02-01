<script setup lang="ts">
import { computed, ref } from 'vue'

import { useSettingsStore } from '@/stores/settings'
import { useSnackbarStore } from '@/stores/snackbar'

import { storeToRefs } from 'pinia'

const props = defineProps<{ modelValue: boolean }>()

const emit = defineEmits(['update:modelValue'])

const setCircularsPassword = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { circularsPassword } = storeToRefs(useSettingsStore())
const inputShow = ref(false)

const snackbarStore = useSnackbarStore()
const { displaySnackbar } = snackbarStore

function closeDialog() {
  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    displaySnackbar('Geslo je pravilno')
  } else {
    if (circularsPassword.value !== '') {
      displaySnackbar('Geslo je napačno')
      circularsPassword.value = ''
    }
  }

  setCircularsPassword.value = false
}
</script>

<template>
  <v-dialog v-model="setCircularsPassword" width="35rem">
    <v-card>
      <v-card-title class="bg-green">VPIŠITE GESLO</v-card-title>
      <v-card-text>
        <p>
          Za ogled okrožnic znotraj aplikacije je potrebno geslo. Geslo je dostopno na <a href="https://ucilnica.gimvic.org/">spletni učilnici</a>.
        </p> <br>
        <v-text-field
          v-model="circularsPassword"
          color="green"
          label="Geslo"
          :append-icon="inputShow ? 'mdi-eye' : 'mdi-eye-off'"
          :type="inputShow ? 'text' : 'password'"
          @click:append="inputShow = !inputShow"
        />
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn color="green" @click="closeDialog()" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
