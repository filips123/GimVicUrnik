<script setup lang="ts">
import { useDocumentsStore } from '@/stores/documents'
import { tokenizeUrl, formatDate } from '@/composables/documents'

document.title = import.meta.env.VITE_TITLE + '- Okrožnice'

const documentsStore = useDocumentsStore()

documentsStore.updateDocuments()

const circulars =
  documentsStore.documents
    ?.filter((document) => document.type === 'circular' || document.type === 'other')
    .reverse() || []

const documentDialogs = {}
// :href="tokenizeUrl(circular.url)"
</script>

<template>
  <v-card class="circulars">
    <v-list>
      <v-item-group>
        <v-list-item v-for="circular in circulars" class="mb-4">
          <v-list-item-title>{{ circular.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ formatDate(new Date(circular.created)) }}</v-list-item-subtitle>
          <!--<v-lazy v-if="circular.content">-->
          <v-dialog width="500">
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" icon="mdi-text-box-outline" flat></v-btn>
            </template>
            <template v-slot:default="{ isActive }">
              <v-card>
                <v-card-title>
                  <span class="text-h5 word-wrap">{{ circular.title }}</span>
                </v-card-title>
                <v-card-text>
                  <div class="con" v-html="circular.content"></div>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn color="green" @click="isActive.value = false">Zapri</v-btn>
                </v-card-actions>
              </v-card>
            </template>
          </v-dialog>
          <!--</v-lazy>-->
        </v-list-item>
      </v-item-group>
    </v-list>
  </v-card>
</template>

<style>
.circulars {
  padding: 16px 4px;
  margin: 0 auto;
  max-width: 40rem;
}
</style>
