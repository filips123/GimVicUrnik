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
  <v-dialog v-model="setDataCollection">
    <v-card title="Nastavite zbiranje podatkov">
      <v-card-text>
        <p>
          Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in
          izboljšanja učinkovitosti. Podatki se ne uporabljajo za identfikacijo uporabnikov,
          oglaševanje ali druge namene.
        </p>
        <v-divider />
        <v-checkbox v-model="dataCollection" label="Zbiranje tehničnih podatkov" />
      </v-card-text>
      <v-card-actions>
        <v-btn @click="setDataCollection = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
