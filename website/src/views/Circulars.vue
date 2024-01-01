<script setup lang="ts">
import { ref } from 'vue'

import { useDocumentsStore, type Document } from '@/stores/documents'
import { tokenizeUrl } from '@/composables/documents'
import { localizeDate } from '@/composables/localization'

document.title = import.meta.env.VITE_TITLE + ' - Okrožnice'

const documentsStore = useDocumentsStore()
const { documents } = documentsStore
documentsStore.updateDocuments()

const circularDialog = ref(false)

const circulars =
  documents?.filter((document) => ['circular', 'other'].includes(document.type)).reverse() || []

let circular: Document = {} as Document

function handleDialog(clickedCircular: Document, event: Event) {
  if ((event?.target as HTMLInputElement)?.classList.contains('mdi-open-in-new')) return

  circular = clickedCircular
  circularDialog.value = true
}
</script>

<template>
  <v-card class="mx-auto" style="max-width: 40rem">
    <v-list>
      <v-list-item
        class="mb-4"
        v-for="circular in circulars"
        :key="circular.title"
        :title="circular.title"
        :subtitle="localizeDate(circular.created)"
        @click="handleDialog(circular, $event)"
      >
        <template #append>
          <v-btn variant="text" icon="mdi-open-in-new" :href="tokenizeUrl(circular.url)" />
        </template>
      </v-list-item>
    </v-list>
  </v-card>

  <v-dialog v-model="circularDialog" scrollable width="42rem">
    <v-card :title="circular.title">
      <v-card-text>
        <div v-html="circular.content"></div>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="green" @click="circularDialog = false" text="Zapri" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
