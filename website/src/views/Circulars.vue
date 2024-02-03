<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'

import { useDocumentsStore, type Document } from '@/stores/documents'
import { useSettingsStore } from '@/stores/settings'

import { tokenizeUrl } from '@/composables/documents'
import { localizeDate } from '@/composables/localization'

import CircularsPassword from '@/components/CircularsPassword.vue'

const documentsStore = useDocumentsStore()
const { documents } = documentsStore
documentsStore.updateDocuments()

const { circularsPassword } = storeToRefs(useSettingsStore())

const circularDialog = ref(false)
const setCircularsPassword = ref(false)

const circulars =
  documents?.filter((document) => ['circular', 'other'].includes(document.type)).reverse() || []

let circular: Document = {} as Document

function handleDialog(clickedCircular: Document, event: Event) {
  if ((event?.target as HTMLInputElement)?.classList.contains('mdi-open-in-new')) return

  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    circular = clickedCircular
    circularDialog.value = true
  } else {
    setCircularsPassword.value = true
  }
}
</script>

<template>
  <v-card class="mx-auto" style="max-width: 40rem">
    <v-virtual-scroll :items="circulars">
      <template v-slot:default="{ item }">
        <v-list-item
          class="mb-4"
          :key="item.title"
          :title="item.title"
          :subtitle="localizeDate(item.created)"
          @click="handleDialog(item, $event)"
        >
          <template #append>
            <v-btn variant="text" icon="mdi-open-in-new" :href="tokenizeUrl(item.url)" />
          </template>
        </v-list-item>
      </template>
    </v-virtual-scroll>
  </v-card>
  <CircularsPassword v-model="setCircularsPassword" />
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
