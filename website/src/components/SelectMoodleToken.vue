<script setup lang="ts">
import { ref } from 'vue'

import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'

const settingsStore = useSettingsStore()

const { moodleToken } = storeToRefs(settingsStore)
const inputShow = ref(false)
const selectMoodleTokenDialog = ref(false)
</script>

<template>
  <v-input
    class="my-6"
    append-icon="mdi-key"
    :messages="moodleToken ? 'Nastavljen' : 'Ni nastavljen'"
    @click="selectMoodleTokenDialog = true">
    Moodle žeton
  </v-input>

  <v-dialog v-model="selectMoodleTokenDialog" width="35rem">
    <v-card>
      <v-card-title class="bg-green uppercase">IZBERITE MOODLE ŽETON</v-card-title>

      <v-card-text class="text--primary mb-n8">
        <p class="text-justify">
          Nastavljanje Moodle žetona omogoča ogled dokumentov iz spletne učilnice brez dodatne
          prijave. Nastavljanje žetona ni obvezno, vendar se boste pred ogledom dokumentov morda
          morali prijaviti. Žeton lahko pridobite po navodilih iz
          <a
            href="https://github.com/filips123/GimVicUrnik/wiki/Pridobitev-Moodle-žetona"
            target="_blank"
            >dokumentacije projekta</a
          >.
        </p>

        <p class="text-justify mb-6">
          <strong>Opozorilo:</strong> Žetona ne zaupajte nikomur, saj omogoča prijavo v spletno
          učilnico z vašim računom. Žeton se shrani v shrambo spletne aplikacije in se ne pošilja
          strežnikom, razen spletni učilnici. Viden bo v vaši zgodovini brskalnika, zato jo primerno
          zavarujte oziroma skrite.
        </p>

        <v-text-field
          v-model="moodleToken"
          color="green"
          label="Moodle žeton"
          :append-icon="inputShow ? 'mdi-eye' : 'mdi-eye-off'"
          :type="inputShow ? 'text' : 'password'"
          @click:append="inputShow = !inputShow" />
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn color="green" @click="selectMoodleTokenDialog = false">V redu</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
