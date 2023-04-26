<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite razred in izbirne predmete
    </v-toolbar>

    <v-card-text class="text--primary">
      <v-select v-model="selectedClasses"
        :items="availableClasses"
        label="Izberite razred in izbirne predmete"
        color="green"
        multiple />
      <v-switch v-model="saveSelection" class="v-input--reverse" color="green" label="Shrani izbiro:" />
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
      <v-btn color="green" text v-on:click=confirmClasses>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, SettingsModule } from '@/store/modules/settings'
import { StorageModule } from '@/store/modules/storage'
import { displaySnackbar } from '@/utils/snackbar'

@Component
export default class SelectClass extends Vue {
  @Prop() isDialog!: boolean

  selectedClasses: string[] = []
  saveSelection = true

  get availableClasses (): ({value: string, text: string} | string)[] {
    return StorageModule.classList || []
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  confirmClasses (): void {
    if (this.selectedClasses.length === 0) {
      displaySnackbar('Izberite vsaj en razred ali izbirni predmet')
      return
    }

    const selectedClasses = this.selectedClasses.sort()

    if (this.saveSelection) {
      SettingsModule.setSelectedEntity({
        type: EntityType.Class,
        data: selectedClasses
      })
    }

    this.$router.push({ name: 'timetable', params: { type: 'classes', value: selectedClasses.join(',') } })
  }
}
</script>
