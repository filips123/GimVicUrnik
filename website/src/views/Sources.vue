<script setup lang="ts">
import { useDocumentsStore } from '@/stores/documents'

import SourcesList from '@/components/SourcesList.vue'

document.title = import.meta.env.VITE_TITLE + ' - Viri'

const documentsStore = useDocumentsStore()
const { documents } = documentsStore

documentsStore.updateDocuments()

const substitutions = documents?.filter((document) => document.type === 'substitutions').reverse()
const lunchSchedules = documents?.filter((document) => document.type === 'lunch-schedule').reverse()
const menus = documents
  ?.filter((document) => document.type === 'snack-menu' || document.type === 'lunch-menu')
  .reverse()
</script>

<template>
  <SourcesList :documents="substitutions" title="Nadomeščanja" displayed-date="effective" />
  <SourcesList :documents="lunchSchedules" title="Razporedi kosila" displayed-date="effective" />
  <SourcesList
    :documents="menus"
    title="Jedilniki"
    displayed-date="effective"
    display-date-as-week="true"
  />
</template>
