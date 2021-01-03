<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite razred in izbirne predmete
    </v-toolbar>

    <v-card-text class="text--primary">
      <v-select v-model="selectedClasses"
        :items="availableClasses"
        label="Izberite razred in izbirne predmete"
        multiple />
      <v-switch v-model="saveSelection" class="v-input--reverse" color="green" label="Shrani izbiro:" />
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
      <v-btn color="green" text v-on:click=confirmClasses>V redu</v-btn>
    </v-card-actions>

    <v-snackbar v-model="displaySnackbar">
      Izberite vsaj en razred ali izbirni predmet
    </v-snackbar>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, SettingsModule } from '@/store/modules/settings'
import { StorageModule } from '@/store/modules/storage'

@Component
export default class SelectClass extends Vue {
  @Prop() isDialog!: boolean

  availableClasses = StorageModule.classList
  selectedClasses: string[] = []
  saveSelection = true
  displaySnackbar = false

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  confirmClasses (): void {
    if (this.selectedClasses.length === 0) {
      this.displaySnackbar = true
      return
    }

    if (this.saveSelection) {
      SettingsModule.setSelectedEntity({
        type: EntityType.Class,
        data: this.selectedClasses
      })
    }

    this.$router.push({ name: 'timetable', params: { type: 'classes', value: this.selectedClasses.join(',') } })
  }
}
</script>
