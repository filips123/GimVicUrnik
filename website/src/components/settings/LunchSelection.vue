<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite vrsto kosila
    </v-toolbar>

    <v-card-text class="text--primary mb-n12">
      <v-radio-group v-model="lunchSelection">
        <v-radio :key="0" :value="0" class="pb-2" color="green" label="Navadno" />
        <v-radio :key="1" :value="1" color="green" label="Vegetarijansko" />
      </v-radio-group>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { LunchType, SettingsModule } from '@/store/modules/settings'

@Component
export default class LunchSelection extends Vue {
  get lunchSelection (): number {
    switch (SettingsModule.selectedMenu?.lunch) {
      case LunchType.Vegetarian:
        return 1
      default:
        return 0
    }
  }

  set lunchSelection (lunch: number) {
    switch (lunch) {
      case 1:
        SettingsModule.setSelectedMenuLunch(LunchType.Vegetarian)
        break
      default:
        SettingsModule.setSelectedMenuLunch(LunchType.Normal)
    }
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
