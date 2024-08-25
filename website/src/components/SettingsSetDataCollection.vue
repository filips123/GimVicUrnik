<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { watch } from 'vue'

import CommonAbout from '@/components/CommonAbout.vue'
import { useSettingsStore } from '@/stores/settings'

const dialog = defineModel<boolean>()

const { dataCollectionCrashes, dataCollectionPerformance } = storeToRefs(useSettingsStore())

watch(dataCollectionPerformance, enabled => {
  // Enable crashes collection along with performance
  if (enabled) dataCollectionCrashes.value = true
})
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card title="Nastavite zbiranje podatkov">
      <template #text>
        <CommonAbout show-data-collection class="pb-1" />
        <v-checkbox
          v-model="dataCollectionPerformance"
          :disabled="false"
          label="Merjenje učinkovitosti"
        />
        <v-checkbox
          v-model="dataCollectionCrashes"
          :disabled="dataCollectionPerformance"
          label="Zbiranje napak"
        />
      </template>
      <template #actions>
        <v-btn text="V redu" @click="dialog = false" />
      </template>
    </v-card>
  </v-dialog>
</template>
