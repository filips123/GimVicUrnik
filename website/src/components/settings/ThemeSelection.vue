<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite barvno temo
    </v-toolbar>

    <v-card-text class="text--primary mb-n12">
      <v-radio-group v-model="themeSelection">
        <v-radio class="pb-2"
          :key="0"
          :value="0"
          label="Sistemska" />

        <v-radio class="pb-2"
          :key="1"
          :value="1"
          label="Svetla" />

        <v-radio
          :key="2"
          :value="2"
          label="Temna" />
      </v-radio-group>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule, ThemeType } from '@/store/modules/settings'

@Component
export default class ThemeSelection extends Vue {
  get themeSelection (): number {
    switch (SettingsModule.theme) {
      case ThemeType.Light:
        return 1
      case ThemeType.Dark:
        return 2
      default:
        return 0
    }
  }

  set themeSelection (theme: number) {
    switch (theme) {
      case 1:
        SettingsModule.setTheme(ThemeType.Light)
        this.$vuetify.theme.dark = false
        break
      case 2:
        SettingsModule.setTheme(ThemeType.Dark)
        this.$vuetify.theme.dark = true
        break
      default:
        this.$vuetify.theme.dark = window.matchMedia('(prefers-color-scheme: dark)').matches
        SettingsModule.setTheme(ThemeType.System)
    }

    // Also set body color to make it possible for browser to style scrollbars
    setTimeout(() => {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      document.getElementsByTagName('body')[0].style.background = getComputedStyle(document.getElementById('app'))['background-color']
    }, 0)
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
