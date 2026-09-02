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

const selected = ref({} as Document)
const action = ref<'content' | 'link'>('content')

const isUnlocked = computed(
  () =>
    !import.meta.env.VITE_CIRCULARS_PASSWORD ||
    circularsPassword.value === import.meta.env.VITE_CIRCULARS_PASSWORD,
)

function handleDialog(circular: Document) {
  selected.value = circular
  action.value = 'content'

  if (isUnlocked.value) {
    contentDialog.value = true
  } else {
    passwordDialog.value = true
  }
}

function handleLink(circular: Document) {
  if (!isUnlocked.value) {
    selected.value = circular
    action.value = 'link'

    passwordDialog.value = true
  }
}

function onAuth() {
  switch (action.value) {
    case 'content':
      contentDialog.value = true
      break
    case 'link':
      window.open(tokenizeUrl(selected.value.url, moodleToken.value), '_blank')
      break
  }
}

const circulars = computed(() => filterDocuments(['circular', 'other']))
</script>

<template>
  <v-column>
    <v-lazy v-for="circular in circulars" :key="circular.url" height="48">
      <v-list-item
        :title="circular.title"
        :subtitle="localizeDate(circular.created)"
        :aria-label="circular.title"
        :href="!circular.content && isUnlocked ? tokenizeUrl(circular.url, moodleToken) : undefined"
        :target="!circular.content && isUnlocked ? '_blank' : undefined"
        class="circular-item"
        height="48"
        @click="circular.content ? handleDialog(circular) : handleLink(circular)"
      >
        <template v-if="circular.content" #append>
          <v-btn-icon
            :icon="mdiOpenInNew"
            :href="isUnlocked ? tokenizeUrl(circular.url, moodleToken) : undefined"
            :target="isUnlocked ? '_blank' : undefined"
            alt="Odpri dokument"
            title="Odpri dokument"
            aria-label="Odpri dokument"
            @click.stop="handleLink(circular)"
            @keydown.stop
          />
        </template>
      </v-list-item>
    </v-lazy>
  </v-column>

  <CircularsPassword v-model="passwordDialog" @update:callback="onAuth" />

  <v-dialog v-model="contentDialog">
    <v-card :title="selected.title">
      <template #text>
        <!-- This is fine because we assume circulars content is safe -->
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="circular-content" v-html="selected.content" />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="contentDialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>

<style>
/* Make items correctly positioned */

.circular-item {
  padding: 0;
}

.circular-item > .v-list-item__overlay {
  border-radius: 4px;
  margin-left: -8px;
  margin-right: -8px;
}

.circular-item > .v-list-item__append {
  margin-right: -8px;
}

.circular-item::after,
.circular-item .v-ripple__container {
  border-radius: 4px;
  width: calc(100% + 16px);
  left: -8px;
}

.circular-item .v-ripple__animation {
  left: 8px;
  scale: 1.2;
}

/* Make tables in content nicer */

.circular-content table {
  width: 100%;
  margin: 10px 0 16px;
  font-size: 14px;
  border-collapse: collapse;
  padding-bottom: 120px;
}

.circular-content th,
.circular-content td {
  border: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  padding: 4px;
}
</style>
