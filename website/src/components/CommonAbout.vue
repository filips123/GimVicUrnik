<script setup lang="ts">
defineProps<{
  showDescription?: boolean
  showDisclaimer?: boolean
  showInstructions?: boolean
  showDataCollection?: boolean
  showDevelopers?: boolean
  showFeedback?: boolean
  showLongFeedback?: boolean
}>()
</script>

<template>
  <div>
    <p v-if="showDescription">
      Spletna aplikacija <em>Urnik Gimnazije Vič</em> prikazuje urnik, nadomeščanja, jedilnik ter
      razpored kosila za dijake in profesorje Gimnazije Vič.
    </p>
    <p v-if="showDisclaimer">
      Aplikacija je neuradna in lahko vsebuje nepopolne ali napačne podatke. Za ogled uradnih
      podatkov uporabite
      <a href="https://ucilnica.gimvic.org/" target="_blank">Spletno učilnico Gimnazije Vič</a>.
    </p>
    <p v-if="showInstructions">
      Navodila za namestitev in uporabo so na voljo v
      <a href="https://github.com/filips123/GimVicUrnik/wiki" target="_blank">dokumentaciji</a>.
    </p>
    <p v-if="showDataCollection">
      Aplikacija s pomočjo storitve
      <a href="https://sentry.io/privacy/" target="_blank">Sentry</a> zbira omejene podatke o
      napravi in uporabi za namene odpravljanja napak ter izboljšanja učinkovitosti. Podatki se ne
      uporabljajo za identifikacijo uporabnikov, oglaševanje ali druge namene.
    </p>
    <span v-if="showDevelopers">Razvijalci:</span>
    <ul v-if="showDevelopers">
      <li>Filip Štamcar</li>
      <li>Jakob Kralj</li>
      <li>Peter Jereb</li>
    </ul>
    <p v-if="showFeedback">
      Če ste odkrili napako v aplikaciji ali podatkih, želite prispevati k razvoju ali ponuditi
      povratne informacije, lahko to naredite na
      <a href="https://github.com/filips123/GimVicUrnik/wiki/Povratne-informacije" target="_blank"
        >uradnem repozitoriju</a
      >.
    </p>
    <div v-if="showLongFeedback">
      <p>Ker se aplikacija stalno razvija, so nam vaše povratne informacije zelo pomembne.</p>
      <p>
        Če ste odkrili napako v aplikaciji ali podatkih, želite prispevati k razvoju ali ponuditi
        povratne informacije, lahko to naredite na
        <a href="https://github.com/filips123/GimVicUrnik/wiki/Povratne-informacije" target="_blank"
          >uradnem repozitoriju</a
        >
        (potreben je brezplačen GitHub račun). Če nimate GitHub računa, lahko povratne informacije
        do nadaljnjega sporočite tudi prek
        <a href="https://forms.gle/Ffhii1NvczBKimB18" target="_blank">vprašalnika</a>, ki je
        dostopen brez prijave. V primeru večjih težav nam lahko pišete na:
        <a href="mailto:gimvicurnik@gmail.com">gimvicurnik@gmail.com</a>.
      </p>
      <p>
        <strong>Pozor:</strong> Žal ne moremo ugoditi vsem vašim predlogom, vendar predlagamo, da si
        že obstoječe funkcije pogledate na
        <a href="https://github.com/filips123/GimVicUrnik/wiki" target="_blank"
          >uradni dokumentaciji</a
        >, saj se jih veliko uporabnikov morda ne zaveda.
      </p>
    </div>
  </div>
</template>
