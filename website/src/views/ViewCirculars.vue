<script setup lang="ts">
import CircularsPassword from '@/components/CircularsPassword.vue'
import { useDocumentsStore, type Document } from '@/stores/documents'
import { useSettingsStore } from '@/stores/settings'
import { tokenizeUrl } from '@/utils/documents'
import { localizeDate } from '@/utils/localization'
import { storeToRefs } from 'pinia'
import { ref } from 'vue'

const documentsStore = useDocumentsStore()
const { filterDocuments, updateDocuments } = documentsStore
updateDocuments()

const { circularsPassword, moodleToken } = storeToRefs(useSettingsStore())

const dialog = ref(false)
const passwordDialog = ref(false)
const circular = ref({} as Document)

function handleDialog(clickedCircular: Document) {
  if (circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD) {
    circular.value = clickedCircular
    dialog.value = true
  } else {
    passwordDialog.value = true
  }
}

const circulars = filterDocuments(['circular', 'other'])
</script>

<template>
  <v-column>
    <v-virtual-scroll :items="circulars">
      <template #default="{ item }">
        <v-list-item
          :key="item.title"
          :title="item.title"
          :subtitle="localizeDate(item.created)"
          @click="handleDialog(item)"
        >
          <template #append>
            <v-btn-icon
              icon="mdi-open-in-new"
              :href="tokenizeUrl(item.url, moodleToken)"
              target="_blank"
              @click.stop
            />
          </template>
        </v-list-item>
      </template>
    </v-virtual-scroll>
  </v-column>
  <CircularsPassword v-model="passwordDialog" />
  <v-dialog v-model="dialog">
    <v-card :title="circular.title">
      <template #text>
        <div v-html="circular.content"></div>
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
