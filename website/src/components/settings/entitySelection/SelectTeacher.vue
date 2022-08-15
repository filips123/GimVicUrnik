<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite profesorja
    </v-toolbar>

    <v-card-text class="text--primary">
      <v-select v-model="selectedTeacher" :items="availableTeachers" label="Izberite profesorja" color="green" />
      <v-switch v-model="saveSelection" class="v-input--reverse" color="green" label="Shrani izbiro:" />
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
      <v-btn color="green" text v-on:click=confirmTeacher>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, SettingsModule } from '@/store/modules/settings'
import { StorageModule } from '@/store/modules/storage'
import { displaySnackbar } from '@/utils/snackbar'

@Component
export default class SelectTeacher extends Vue {
  @Prop() isDialog!: boolean

  selectedTeacher: string | null = null
  saveSelection = true

  get availableTeachers (): ({value: string, text: string} | string)[] {
    return StorageModule.teacherList || []
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  confirmTeacher (): void {
    if (!this.selectedTeacher) {
      displaySnackbar('Izberite profesorja')
      return
    }

    if (this.saveSelection) {
      SettingsModule.setSelectedEntity({
        type: EntityType.Teacher,
        data: [this.selectedTeacher]
      })
    }

    this.$router.push({ name: 'timetable', params: { type: 'teachers', value: this.selectedTeacher } })
  }
}
</script>
