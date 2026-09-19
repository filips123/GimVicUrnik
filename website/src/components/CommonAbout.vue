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
  <div class="d-flex flex-column ga-1">
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
    <div v-if="showDevelopers">
      <p>Razvijalci:</p>
      <ul>
        <li>Filip Štamcar</li>
        <li>Jakob Kralj</li>
        <li>Peter Jereb</li>
      </ul>
    </div>
    <p v-if="showFeedback">
      Če ste odkrili napako v aplikaciji ali podatkih, želite prispevati k razvoju ali ponuditi
      povratne informacije, lahko to storite na
      <a href="https://github.com/filips123/GimVicUrnik/wiki/Povratne-informacije" target="_blank"
        >uradnem repozitoriju</a
      >.
    </p>
    <div v-if="showLongFeedback">
      <p>Ker se aplikacija stalno razvija, so nam vaše povratne informacije zelo pomembne.</p>
      <p>
        Če ste odkrili napako v aplikaciji ali podatkih, želite prispevati k razvoju ali ponuditi
        povratne informacije, lahko to storite na
        <a href="https://github.com/filips123/GimVicUrnik/wiki/Povratne-informacije" target="_blank"
          >uradnem repozitoriju</a
        >
        (potreben je brezplačen GitHub račun). Če nimate GitHub računa, nam lahko povratne
        informacije sporočite tudi prek
        <a href="https://forms.gle/Ffhii1NvczBKimB18" target="_blank">vprašalnika</a>, ki je
        dostopen brez prijave. V primeru večjih težav pa nam lahko pišete na
        <a href="mailto:gimvicurnik@gmail.com" target="_blank">gimvicurnik@gmail.com</a>.
      </p>
      <p>
        Priporočamo še, da preverite
        <a href="https://github.com/filips123/GimVicUrnik/wiki" target="_blank">dokumentacijo</a>,
        kjer so podrobno opisane vse funkcionalnosti aplikacije ter navodila za namestitev in
        uporabo.
      </p>
    </div>
  </div>
</template>
