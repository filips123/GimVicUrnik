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
  <v-dialog v-model="setCircularsPassword">
    <v-card title="Vpišite geslo">
      <v-card-text>
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
        />
      </v-card-text>
      <v-card-actions>
        <v-btn @click="closeDialog()" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
