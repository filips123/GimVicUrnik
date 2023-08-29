<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Aplikacija GimVič
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
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
      <v-btn color="green" text v-on:click=clickedOk>V redu</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class WelcomeInfo extends Vue {
  @Prop() isDialog!: boolean

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  clickedOk (): void {
    this.$emit('clickedOk')
  }
}
</script>
