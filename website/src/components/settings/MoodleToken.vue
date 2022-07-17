<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Nastavite Moodle žeton
    </v-toolbar>

    <v-card-text class="text--primary mb-n8">
      <p class="text-justify">
        Nastavljanje Moodle žetona omogoča ogled dokumentov iz spletne učilnice brez dodatne prijave.
        Nastavljanje žetona ni obvezno, vendar se boste pred ogledom dokumentov morda morali prijaviti.
        Žeton lahko pridobite po navodilih iz <a href="https://github.com/filips123/GimVicUrnik/wiki/Pridobitev-Moodle-žetona" target="_blank">dokumentacije projekta</a>.
      </p>

      <p class="text-justify">
        <strong>Opozorilo:</strong> Žetona ne zaupajte nikomur, saj omogoča prijavo v spletno učilnico z vašim računom.
        Žeton se shrani v shrambo spletne aplikacije in se ne pošilja strežnikom, razen spletni učilnici.
        Viden bo v vaši zgodovini brskalnika, zato jo primerno zavarujte oziroma skrite.
      </p>

      <v-text-field v-model="moodleToken"
        color="green"
        label="Moodle žeton"
        :append-icon="inputShow ? mdiEye : mdiEyeOff"
        :type="inputShow ? 'text' : 'password'"
        @click:append="inputShow = !inputShow" />
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { Component, Vue } from 'vue-property-decorator'

import { SettingsModule } from '@/store/modules/settings'

@Component
export default class MoodleToken extends Vue {
  mdiEye = mdiEye
  mdiEyeOff = mdiEyeOff

  inputShow = false

  get moodleToken (): string | null {
    return SettingsModule.moodleToken
  }

  set moodleToken (token: string | null) {
    SettingsModule.setMoodleToken(token || null)
  }

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
