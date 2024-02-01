<script setup lang="ts">
import { computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'

const props = defineProps<{ modelValue: boolean }>()

const emit = defineEmits(['update:modelValue'])

const setDataCollection = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})

const { dataCollection } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="setDataCollection" width="35rem">
    <v-card>
      <v-card-title class="bg-green">Nastavite zbiranje podatkov</v-card-title>
      <v-card-text>
        <v-checkbox v-model="dataCollection" color="green" label="Zbiranje tehničnih podatkov" />
        <p>
          Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in
          izboljšanja učinkovitosti. Podatki se ne uporabljajo za identfikacijo uporabnikov,
          oglaševanje ali druge namene.
        </p>
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn color="green" @click="setDataCollection = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
