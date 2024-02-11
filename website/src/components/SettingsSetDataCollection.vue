<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'

const dialog = defineModel<boolean>()

const { dataCollection } = storeToRefs(useSettingsStore())
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Nastavite zbiranje podatkov">
      <template #text>
        <p>
          Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in
          izboljšanja učinkovitosti. Podatki se ne uporabljajo za identfikacijo uporabnikov,
          oglaševanje ali druge namene.
        </p>
        <v-divider />
        <v-checkbox v-model="dataCollection" label="Zbiranje tehničnih podatkov" />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
