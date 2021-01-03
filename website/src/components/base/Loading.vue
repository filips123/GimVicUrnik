<!-- Component for displaying loading bar -->

<template>
  <v-row align-content="center" class="fill-height px-8 pt-8" justify="center" style="height: 400px;">
    <v-col class="subtitle-1 text-center" cols="12">
      Nalaganje ...
    </v-col>
    <v-col class="col-sm-10 col-md-8 col-lg-6 col-xl-4">
      <v-progress-linear color="green" height="8" indeterminate rounded />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class Loading extends Vue {
}
</script>
