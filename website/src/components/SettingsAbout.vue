<script setup lang="ts">
import CommonAbout from '@/components/CommonAbout.vue'

const dialog = defineModel<boolean>()
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="O aplikaciji">
      <template #text>
        <CommonAbout
          show-description
          show-disclaimer
          show-instructions
          show-data-collection
          show-developers
          show-feedback
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
