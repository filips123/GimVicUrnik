<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite učilnico
    </v-toolbar>

    <v-card-text class="text--primary">
      <v-select v-model="selectedClassroom"
        :item-text="item => item.text"
        :item-value="item => item.value"
        :items="availableClassrooms"
        label="Izberite učilnico"
        color="green" />
      <v-switch v-model="saveSelection" class="v-input--reverse" color="green" label="Shrani izbiro:" />
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
      <v-btn color="green" text v-on:click=confirmClassroom>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { EntityType, SettingsModule } from '@/store/modules/settings'
import { StorageModule } from '@/store/modules/storage'
import { displaySnackbar } from '@/utils/snackbar'

@Component
export default class SelectClassroom extends Vue {
  @Prop() isDialog!: boolean

  selectedClassroom: string | null = null
  saveSelection = true

  get availableClassrooms (): ({value: string, text: string} | string)[] {
    return [{ value: 'empty', text: 'Proste učilnice' }, ...(StorageModule.classroomList || [])]
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  confirmClassroom (): void {
    if (!this.selectedClassroom) {
      displaySnackbar('Izberite učilnico')
      return
    }

    if (this.saveSelection) {
      SettingsModule.setSelectedEntity({
        type: EntityType.Classroom,
        data: [this.selectedClassroom]
      })
    }

    this.$router.push({ name: 'timetable', params: { type: 'classrooms', value: this.selectedClassroom } })
  }
}
</script>
