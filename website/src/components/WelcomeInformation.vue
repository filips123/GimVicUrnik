<script setup lang="ts">
import CommonAbout from '@/components/CommonAbout.vue'

const dialog = defineModel<boolean>()
</script>

<template>
  <v-dialog v-model="dialog" persistent>
    <v-card title="Urnik Gimnazije Vič">
      <template #text>
        <CommonAbout
          show-description
          show-disclaimer
          show-instructions
          show-data-collection
          show-feedback
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
