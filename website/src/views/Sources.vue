<script setup lang="ts">
import { useDocumentsStore } from '@/stores/documents'
import DocumentList from '@/components/DocumentList.vue'

document.title = import.meta.env.VITE_TITLE + '- Viri'

const documentsStore = useDocumentsStore()

documentsStore.updateDocuments()

const substitutions =
  documentsStore.documents?.filter((document) => document.type === 'substitutions').reverse() || []
const lunchSchedules =
  documentsStore.documents?.filter((document) => document.type === 'lunch-schedule').reverse() || []
const menus =
  documentsStore.documents
    ?.filter((document) => document.type === 'snack-menu' || document.type === 'lunch-menu')
    .reverse() || []
</script>

<template>
  <document-list :documents="substitutions" title="Nadomeščanja" displayed-date="effective" />
  <document-list :documents="lunchSchedules" title="Razporedi kosila" displayed-date="effective" />
  <document-list
    :documents="menus"
    title="Jedilniki"
    displayed-date="effective"
    display-date-as-week="true" />
</template>
