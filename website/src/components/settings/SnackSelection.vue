<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite vrsto malice
    </v-toolbar>

    <v-card-text class="text--primary mb-n12">
      <v-radio-group v-model="snackSelection">
        <v-radio :key="0" :value="0" class="pb-2" color="green" label="Navadna" />
        <v-radio :key="1" :value="1" class="pb-2" color="green" label="Vegetarijanska" />
        <v-radio :key="2" :value="2" class="pb-2" color="green" label="Vegetarijanska s perutnino in ribo" />
        <v-radio :key="3" :value="3" color="green" label="Sadnozelenjavna" />
      </v-radio-group>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule, SnackType } from '@/store/modules/settings'

@Component
export default class SnackSelection extends Vue {
  get snackSelection (): number {
    switch (SettingsModule.selectedMenu?.snack) {
      case SnackType.Vegetarian:
        return 1
      case SnackType.Poultry:
        return 2
      case SnackType.Fruitvegetable:
        return 3
      default:
        return 0
    }
  }

  set snackSelection (snack: number) {
    switch (snack) {
      case 1:
        SettingsModule.setSelectedMenuSnack(SnackType.Vegetarian)
        break
      case 2:
        SettingsModule.setSelectedMenuSnack(SnackType.Poultry)
        break
      case 3:
        SettingsModule.setSelectedMenuSnack(SnackType.Fruitvegetable)
        break
      default:
        SettingsModule.setSelectedMenuSnack(SnackType.Normal)
    }
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
