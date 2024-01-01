<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ modelValue: boolean }>()

const emit = defineEmits(['update:modelValue'])

const about = computed({
  get() {
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
  },
})
</script>

<template>
  <v-dialog v-model="about" width="35rem">
    <v-card>
      <v-card-title class="bg-green">O APLIKACIJI</v-card-title>
      <v-card-text>
        <p>
          Aplikacija GimVič prikazuje urnik, nadomeščanja, jedilnik ter razpored kosila za dijake in
          profesorje Gimnazije Vič.
        </p>
        <p>
          Aplikacija je neuradna in lahko vsebuje nepopolne ali napačne podatke. Za ogled uradnih
          podatkov uporabite
          <a href="https://ucilnica.gimvic.org/"> Spletno učilnico Gimnazije Vič </a> .
        </p>
        <p>
          V <a href="https://github.com/filips123/GimVicUrnik/wiki"> dokumentaciji projekta </a> so
          dostopna navodila za namestitev in uporabo.
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
          <a href="https://github.com/filips123/GimVicUrnik/issues/new/choose">
            uradnem repozitoriju
          </a>
          .
        </p>
      </v-card-text>
      <v-card-actions class="justify-end">
        <v-btn color="green" @click="about = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
