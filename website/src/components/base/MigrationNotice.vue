<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Nov naslov spletne aplikacije
    </v-toolbar>

    <v-card-text class="text--primary pt-6 mb-n6">
      <p>
        S šolskim letom 2022/23 bo spletna aplikacija {{ title }} dostopna na naslovu <a :href="target" target="_blank">{{ target }}</a>.
      </p>
      <p>
        Trenutno različico boste morali odstraniti ter aplikacijo ponovno namestiti iz novega naslova. Navodila za namestitev
        so dostopna v <a :href="instructions" target="_blank">dokumentaciji projekta</a>.
      </p>
      <p>
        Podatki na obstoječi različici se bodo prenehali posodabljati, sčasoma pa bo ukinjena, zato prehod na novo opravite čim prej.
        Nova različica ohranja vse funkcionalnosti obstoječe, dodaja pa tudi nekatere novosti in izboljšanje stabilnosti.
      </p>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn color="green" text v-on:click=closeDialog>Skrij obvestilo</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class MigrationNotice extends Vue {
  title = process.env.VUE_APP_TITLE
  target = process.env.VUE_APP_MIGRATION_TARGET
  instructions = process.env.VUE_APP_MIGRATION_INSTRUCTIONS

  closeDialog (): void {
    this.$emit('closeDialog')
  }
}
</script>
