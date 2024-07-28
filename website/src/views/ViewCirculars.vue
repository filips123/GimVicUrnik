<script setup lang="ts">
import { mdiOpenInNew } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { computed, ref } from 'vue'

import CircularsPassword from '@/components/CircularsPassword.vue'
import { type Document, useDocumentsStore } from '@/stores/documents'
import { useSettingsStore } from '@/stores/settings'
import { tokenizeUrl } from '@/utils/documents'
import { localizeDate } from '@/utils/localization'

const { circularsPassword, moodleToken } = storeToRefs(useSettingsStore())
const { filterDocuments, updateDocuments } = useDocumentsStore()

updateDocuments()

const contentDialog = ref(false)
const passwordDialog = ref(false)
const circular = ref({} as Document)

function handleDialog(clickedCircular: Document) {
  circular.value = clickedCircular

  if (
    !import.meta.env.VITE_CIRCULARS_PASSWORD ||
    circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD
  ) {
    passwordDialog.value = false
    contentDialog.value = true
  } else {
    contentDialog.value = false
    passwordDialog.value = true
  }
}

const circulars = computed(() => filterDocuments(['circular', 'other']))
</script>

<template>
  <v-column>
    <v-virtual-scroll :items="circulars">
      <template #default="{ item }">
        <v-list-item
          :key="item.url"
          :title="item.title"
          :subtitle="localizeDate(item.created)"
          :aria-label="item.title"
          :href="item.content ? undefined : tokenizeUrl(item.url, moodleToken)"
          :target="item.content ? undefined : '_blank'"
          @[item.content&&`click`]="handleDialog(item)"
        >
          <template v-if="item.content" #append>
            <v-btn-icon
              :icon="mdiOpenInNew"
              :href="tokenizeUrl(item.url, moodleToken)"
              target="_blank"
              alt="Odpri dokument"
              title="Odpri dokument"
              aria-label="Odpri dokument"
              @click.stop
              @keydown.stop
            />
          </template>
        </v-list-item>
      </template>
    </v-virtual-scroll>
  </v-column>

  <CircularsPassword v-model="passwordDialog" v-model:callback="contentDialog" />

  <v-dialog v-model="contentDialog">
    <v-card :title="circular.title">
      <template #text>
        <!-- This is fine because we assume circulars content is safe -->
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div v-html="circular.content" />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="contentDialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
