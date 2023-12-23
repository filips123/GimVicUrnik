<script setup lang="ts">
import { ref, computed } from 'vue'

import type { Document } from '@/stores/documents'

import { useDocumentsStore } from '@/stores/documents'
import { tokenizeUrl, formatDate } from '@/composables/documents'

document.title = import.meta.env.VITE_TITLE + '- Okrožnice'

const documentsStore = useDocumentsStore()
documentsStore.updateDocuments()

const DocumentDialog = ref(false)

const circulars = computed(
  () =>
    documentsStore.documents
      ?.filter((document) => document.type === 'circular' || document.type === 'other')
      .reverse() || []
)

let circularDialog: Document = {} as Document

function handleDialog(circular: Document, event: Event) {
  if ((event?.target as HTMLInputElement)?.classList.contains('mdi-open-in-new')) {
    return
  }

  circularDialog = circular
  DocumentDialog.value = true
}

// Load first 10-20 circular and add "more" button
</script>

<template>
  <v-lazy :min-height="100">
    <v-card class="circulars">
      <v-list>
        <v-list-item
          v-for="circular in circulars"
          :title="circular.title"
          :subtitle="formatDate(new Date(circular.created))"
          class="mb-4"
          @click="handleDialog(circular, $event)">
          <template v-slot:append>
            <v-btn icon="mdi-open-in-new" variant="text" :href="tokenizeUrl(circular.url)" />
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </v-lazy>

  <v-dialog v-model="DocumentDialog" scrollable width="42rem">
    <v-card>
      <v-card-title>
        <span class="text-h5 text-wrap">{{ circularDialog.title }}</span>
      </v-card-title>
      <v-card-text>
        <div v-html="circularDialog.content"></div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="green" @click="DocumentDialog = false">Zapri</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style>
.circulars {
  padding: 16px 4px;
  margin: 0 auto;
  max-width: 40rem;
}
</style>
