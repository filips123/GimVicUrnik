<script setup lang="ts">
import { mdiEye, mdiEyeOff } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

import { useSettingsStore } from '@/stores/settings'

const dialog = defineModel<boolean>()

const { moodleToken } = storeToRefs(useSettingsStore())

const inputShow = ref(false)
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Nastavite Moodle žeton">
      <template #text>
        <p>
          Nastavljanje Moodle žetona omogoča ogled dokumentov iz spletne učilnice brez dodatne
          prijave. Nastavljanje žetona ni obvezno, vendar se boste sicer pred ogledom dokumentov
          morda morali prijaviti. Žeton lahko pridobite po navodilih iz
          <a
            href="https://github.com/filips123/GimVicUrnik/wiki/Pridobitev-Moodle-žetona"
            target="_blank"
            >dokumentacije</a
          >.
        </p>
        <p class="pb-4">
          <strong>Opozorilo:</strong> Žetona ne zaupajte nikomur, saj omogoča prijavo v spletno
          učilnico z vašim računom. Žeton se shrani v shrambo spletne aplikacije in se ne pošilja
          strežnikom, razen spletni učilnici. Viden bo v vaši zgodovini brskalnika, zato jo primerno
          zavarujte oziroma skrite.
        </p>
        <v-text-field
          v-model="moodleToken"
          label="Moodle žeton"
          :append-inner-icon="inputShow ? mdiEye : mdiEyeOff"
          :type="inputShow ? 'text' : 'password'"
          autofocus
          @click:append-inner="inputShow = !inputShow"
          @keydown.enter="dialog = false"
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
