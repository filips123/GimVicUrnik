<script setup lang="ts">
import TextAbout from '@/components/TextAbout.vue'

const dialog = defineModel<boolean>()
</script>

<template>
  <v-dialog v-model="dialog" persistent>
    <v-card title="Urnik Gimnazije Vič">
      <template #text>
        <TextAbout show-description show-disclaimer show-instructions show-data-collection />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
