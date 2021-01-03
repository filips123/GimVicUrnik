<template>
  <v-card width="35rem">
    <v-toolbar class="text-uppercase" color="#009300" dark>
      Izberite pogled
    </v-toolbar>

    <v-card-text class="text--primary" style="text-align: center; margin-bottom: -20px;">
      <v-btn class="mt-1" color="green" text v-on:click=selectedClass>Razred</v-btn>
      <v-btn class="mt-1" color="green" text v-on:click=selectedTeacher>Profesor</v-btn>
      <v-btn class="mt-1" color="green" text v-on:click=selectedClassroom>Učilnica</v-btn>
    </v-card-text>

    <v-card-actions class="justify-end">
      <v-btn v-if="isDialog" color="green" text v-on:click=closeDialog>Zapri</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class SelectType extends Vue {
  @Prop() isDialog!: boolean

  closeDialog (): void {
    this.$emit('closeDialog')
  }

  selectedClass (): void {
    this.$emit('selectedClass')
  }

  selectedTeacher (): void {
    this.$emit('selectedTeacher')
  }

  selectedClassroom (): void {
    this.$emit('selectedClassroom')
  }
}
</script>
