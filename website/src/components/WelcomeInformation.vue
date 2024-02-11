<script setup lang="ts">
const dialog = defineModel<boolean>()
</script>

<template>
  <v-dialog v-model="dialog" persistent>
    <v-card title="Aplikacija GimVič">
      <template #text>
        <p>
          Aplikacija GimVič prikazuje urnik, nadomeščanja, jedilnik ter razpored kosila za dijake in
          profesorje Gimnazije Vič.
        </p>
        <p>
          Aplikacija je neuradna in lahko vsebuje nepopolne ali napačne podatke. Za ogled uradnih
          podatkov uporabite
          <a href="https://ucilnica.gimvic.org/"> Spletno učilnico Gimnazije Vič</a>.
        </p>
        <p>
          V
          <a href="https://github.com/filips123/GimVicUrnik/wiki"> dokumentaciji projekta</a> so
          dostopna navodila za namestitev in uporabo.
        </p>
        <p>
          Aplikacija zbira omejene podatke o brskalniku in uporabi za namene odpravljanja napak in
          izboljšanja učinkovitosti. Podatki se ne uporabljajo za identfikacijo uporabnikov,
          oglaševanje ali druge namene.
        </p>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
