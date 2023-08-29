<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      O aplikaciji
    </v-toolbar>

    <v-card-text class="text--primary">
      <p>
        Aplikacija GimVič prikazuje urnik, nadomeščanja, jedilnik ter razpored kosila za dijake in profesorje Gimnazije Vič.
      </p>
      <p>
        Aplikacija je neuradna in lahko vsebuje nepopolne ali napačne podatke. Za ogled uradnih podatkov uporabite
        <a class="text-decoration-none" href="https://ucilnica.gimvic.org/">Spletno učilnico Gimnazije Vič</a>.
      </p>
      <p>
        V <a class="text-decoration-none" href="https://github.com/filips123/GimVicUrnik/wiki">dokumentaciji projekta</a>
        so dostopna navodila za namestitev in uporabo.
      </p>
      <p>
        Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in izboljšanja učinkovitosti.
        Podatki se ne uporabljajo za identfikacijo uporabnikov, oglaševanje ali druge namene.
      </p>
      <p>
        Razvijalci:
        <ul>
          <li>Filip Štamcar</li>
          <li>Jakob Kralj</li>
          <li>Peter Jereb</li>
        </ul>
      </p>
      <p>
        Če ste odkrili napako v aplikaciji ali morda želite ponuditi povratne informacije, lahko to naredite na
        <a class="text-decoration-none" href="https://github.com/filips123/GimVicUrnik/issues/new/choose">uradnem repozitoriju</a>.
      </p>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class About extends Vue {
  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
