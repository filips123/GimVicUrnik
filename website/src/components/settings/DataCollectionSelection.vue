<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Nastavite zbiranje podatkov
    </v-toolbar>

    <v-card-text class="text--primary mb-n8">
      <v-checkbox v-model="performanceCollection" class="mb-n3" color="green" label="Merjenje učinkovitosti" />
      <v-checkbox v-model="crashesCollection" color="green" label="Zbiranje napak" :disabled="performanceCollection" />

      <p class="text-justify">
        Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in izboljšanja učinkovitosti.
        Podatki se ne uporabljajo za identfikacijo uporabnikov, oglaševanje ali druge namene.
      </p>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'

@Component
export default class DataCollectionSelection extends Vue {
  get performanceCollection (): boolean {
    return SettingsModule.dataCollection.performance
  }

  set performanceCollection (performance: boolean) {
    if (performance) this.crashesCollection = true
    SettingsModule.setDataCollectionPerformance(performance)
  }

  get crashesCollection (): boolean {
    return SettingsModule.dataCollection.performance || SettingsModule.dataCollection.crashes
  }

  set crashesCollection (crashes: boolean) {
    SettingsModule.setDataCollectionCrashes(crashes)
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
