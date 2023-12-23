<script setup lang="ts">
import { ref } from 'vue'

const aboutDialog = ref(false)
</script>

<template>
  <v-input
    class="my-6"
    append-icon="mdi-information-outline"
    :messages="'TODO VERZIJA'"
    @click="aboutDialog = true">
    O Aplikaciji
  </v-input>

  <v-dialog v-model="aboutDialog" width="35rem">
    <v-card width="35rem">
      <v-card-title class="bg-green uppercase">O APLIKACIJI</v-card-title>

      <v-card-text class="text--primary">
        <p>
          Aplikacija GimVič prikazuje urnik, nadomeščanja, jedilnik ter razpored kosila za dijake in
          profesorje Gimnazije Vič.
        </p>
        <p>
          Aplikacija je neuradna in lahko vsebuje nepopolne ali napačne podatke. Za ogled uradnih
          podatkov uporabite
          <a class="text-decoration-none" href="https://ucilnica.gimvic.org/"
            >Spletno učilnico Gimnazije Vič</a
          >.
        </p>
        <p>
          V
          <a class="text-decoration-none" href="https://github.com/filips123/GimVicUrnik/wiki"
            >dokumentaciji projekta</a
          >
          so dostopna navodila za namestitev in uporabo.
        </p>
        <p>
          Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in
          izboljšanja učinkovitosti. Podatki se ne uporabljajo za identfikacijo uporabnikov,
          oglaševanje ali druge namene.
        </p>
        <p>
          Razvijalci:
          <li>Filip Štamcar</li>
          <li>Jakob Kralj</li>
          <li>Peter Jereb</li>
        </p>
        <p>
          Če ste odkrili napako v aplikaciji ali morda želite ponuditi povratne informacije, lahko
          to naredite na
          <a
            class="text-decoration-none"
            href="https://github.com/filips123/GimVicUrnik/issues/new/choose"
            >uradnem repozitoriju</a
          >.
        </p>
      </v-card-text>

      <v-card-actions class="justify-end">
        <v-btn color="green" @click="aboutDialog = false">V redu</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
