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
  <div class="column-layout">
    <v-virtual-scroll :items="circulars">
      <template v-slot:default="{ item }">
        <v-list-item
          :key="item.title"
          :title="item.title"
          :subtitle="localizeDate(item.created)"
          @click="handleDialog(item, $event)"
        >
          <template #append>
            <v-btn-icon icon="mdi-open-in-new" :href="tokenizeUrl(item.url)" />
          </template>
        </v-list-item>
      </template>
    </v-virtual-scroll>
  </div>
  <CircularsPassword v-model="setCircularsPassword" />
  <v-dialog v-model="circularDialog">
    <v-card :title="circular.title">
      <v-card-text>
        <div v-html="circular.content"></div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="circularDialog = false" text="V redu" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
