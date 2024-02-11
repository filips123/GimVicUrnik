<script setup lang="ts">
import SourcesExpansionPanel from '@/components/SourcesExpansionPanel.vue'
import { useDocumentsStore } from '@/stores/documents'

const documentsStore = useDocumentsStore()

const { filterDocuments, updateDocuments } = documentsStore
updateDocuments()

const substitutions = filterDocuments(['substitutions'])
const lunchSchedules = filterDocuments(['lunch-schedule'])
const menus = filterDocuments(['snack-menu', 'lunch-menu'])
</script>

<template>
  <SourcesExpansionPanel title="Nadomeščanja" :documents="substitutions" />
  <SourcesExpansionPanel title="Razporedi kosila" :documents="lunchSchedules" />
  <SourcesExpansionPanel title="Jedilniki" :documents="menus" date-as-week />
</template>
