<script setup lang="ts">
import { mdiBookOpenPageVariantOutline, mdiDelete, mdiPlus } from '@mdi/js'
import { ref, watch } from 'vue'
import { useDisplay } from 'vuetify'

import { useSnackbarStore } from '@/composables/snackbar'
import type { SportSlug, SportsRule } from '@/stores/sports'
import { useSportsStore } from '@/stores/sports'

const props = defineProps<{ sport: SportSlug; rules: SportsRule[]; editable: boolean }>()
const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const { mobile } = useDisplay()
const dialog = ref(false)
const editing = ref(false)
const loading = ref(false)
const draft = ref<{ text: string; url: string | null }[]>([])

watch(
  () => props.rules,
  rules => {
    if (!editing.value) draft.value = rules.map(rule => ({ text: rule.text, url: rule.url }))
  },
  { immediate: true, deep: true },
)

function startEditing() {
  draft.value = props.rules.map(rule => ({ text: rule.text, url: rule.url }))
  editing.value = true
}

async function save() {
  if (!window.confirm('Želite shraniti spremenjena pravila za to sezono?')) return
  loading.value = true
  try {
    await sportsStore.saveRules(props.sport, draft.value)
    editing.value = false
    displaySnackbar('Pravila so shranjena')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Pravil ni bilo mogoče shraniti')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <template v-if="mobile">
    <v-btn
      :icon="mdiBookOpenPageVariantOutline"
      title="Pravila"
      aria-label="Pravila"
      color="secondary"
      class="rules-fab"
      elevation="5"
      @click="dialog = true"
    />
    <v-dialog v-model="dialog" max-width="650">
      <v-card title="Pravila">
        <v-card-text class="rules-dialog-content">
          <template v-if="!editing">
            <ol class="sports-rules">
              <li v-for="rule in rules" :key="rule.position">
                {{ rule.text }}
                <a v-if="rule.url" :href="rule.url" target="_blank" rel="noopener">
                  Posnetek pravil
                </a>
              </li>
            </ol>
            <v-btn
              v-if="editable"
              text="Uredi pravila"
              color="secondary"
              variant="outlined"
              @click="startEditing"
            />
          </template>
          <template v-else>
            <div v-for="(rule, index) in draft" :key="index" class="d-flex ga-2 mb-3 align-start">
              <div class="flex-grow-1">
                <v-textarea v-model="rule.text" :label="`Pravilo ${index + 1}`" rows="2" />
                <v-text-field v-model="rule.url" label="Povezava (neobvezno)" />
              </div>
              <v-btn
                :icon="mdiDelete"
                title="Odstrani pravilo"
                variant="text"
                @click="draft.splice(index, 1)"
              />
            </div>
            <v-btn
              :prepend-icon="mdiPlus"
              text="Dodaj pravilo"
              color="secondary"
              variant="outlined"
              class="mr-2"
              @click="draft.push({ text: '', url: null })"
            />
            <v-btn text="Prekliči" variant="text" @click="editing = false" />
            <v-btn text="Shrani" color="secondary" :loading="loading" @click="save" />
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text="Zapri" @click="dialog = false" />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>

  <v-expansion-panels v-else class="mt-4">
    <v-expansion-panel title="Pravila">
      <v-expansion-panel-text>
        <template v-if="!editing">
          <ol class="sports-rules">
            <li v-for="rule in rules" :key="rule.position">
              {{ rule.text }}
              <a v-if="rule.url" :href="rule.url" target="_blank" rel="noopener">
                Posnetek pravil
              </a>
            </li>
          </ol>
          <v-btn
            v-if="editable"
            text="Uredi pravila"
            color="secondary"
            variant="outlined"
            @click="startEditing"
          />
        </template>
        <template v-else>
          <div v-for="(rule, index) in draft" :key="index" class="d-flex ga-2 mb-3 align-start">
            <div class="flex-grow-1">
              <v-textarea v-model="rule.text" :label="`Pravilo ${index + 1}`" rows="2" />
              <v-text-field v-model="rule.url" label="Povezava (neobvezno)" />
            </div>
            <v-btn
              :icon="mdiDelete"
              title="Odstrani pravilo"
              variant="text"
              @click="draft.splice(index, 1)"
            />
          </div>
          <v-btn
            :prepend-icon="mdiPlus"
            text="Dodaj pravilo"
            color="secondary"
            variant="outlined"
            class="mr-2"
            @click="draft.push({ text: '', url: null })"
          />
          <v-btn text="Prekliči" variant="text" @click="editing = false" />
          <v-btn text="Shrani" color="secondary" :loading="loading" @click="save" />
        </template>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style scoped>
.sports-rules {
  margin-bottom: 1rem;
}

.sports-rules li {
  margin-bottom: 0.45rem;
}

.rules-fab {
  position: fixed !important;
  right: 1rem !important;
  bottom: 7.75rem !important;
  left: auto !important;
  z-index: 1006;
}

.rules-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
