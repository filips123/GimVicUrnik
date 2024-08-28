<script setup lang="ts">
import { computed } from 'vue'

import SourcesExpansionPanel from '@/components/SourcesExpansionPanel.vue'
import { useDocumentsStore } from '@/stores/documents'

const { filterDocuments, updateDocuments } = useDocumentsStore()

updateDocuments()

const substitutions = computed(() => filterDocuments(['substitutions']))
const lunchSchedules = computed(() => filterDocuments(['lunch-schedule']))
const menus = computed(() => filterDocuments(['snack-menu', 'lunch-menu']))
</script>

<template>
  <v-column>
    <SourcesExpansionPanel title="Nadomeščanja" :documents="substitutions" />
    <SourcesExpansionPanel title="Razporedi kosila" :documents="lunchSchedules" />
    <SourcesExpansionPanel title="Jedilniki" :documents="menus" date-as-week />
  </v-column>
</template>
