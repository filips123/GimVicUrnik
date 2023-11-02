<script setup lang="ts">
import { useDocumentsStore } from '@/stores/documents'
import { tokenizeUrl, formatDate } from '@/composables/documents'

document.title = import.meta.env.VITE_TITLE + '- Okrožnice'

const documentsStore = useDocumentsStore()

documentsStore.updateDocuments()

// Get the circulars
const circulars =
  documentsStore.documents
    ?.filter((document) => document.type === 'circular' || document.type === 'other')
    .reverse() || []
</script>

<template>
  <v-card class="documents">
    <v-list-item v-for="circular in circulars" :href="tokenizeUrl(circular.url)" class="mb-4">
      <v-list-item-title>{{ circular.title }}</v-list-item-title>
      <v-list-item-subtitle>{{ formatDate(new Date(circular.created)) }}</v-list-item-subtitle>
    </v-list-item>
  </v-card>
</template>

<style>
.documents {
  padding: 16px 4px;
  margin: 0 auto;
  max-width: 40rem;
}
</style>
