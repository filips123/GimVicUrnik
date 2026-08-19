<script setup lang="ts">
import { mdiContentSave } from '@mdi/js'
import { computed, ref, watch } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import type { GroupName, SportSlug, SportsSeason } from '@/stores/sports'
import { useSportsStore } from '@/stores/sports'

const props = defineProps<{ sport: SportSlug; season: SportsSeason }>()
const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const groupNames: GroupName[] = ['A', 'B', 'C', 'D']
const loading = ref(false)
const editorPanel = ref<string | undefined>()
const activeGroup = ref<GroupName>('A')
const assignments = ref<Record<string, GroupName | null>>({})

const hasSavedTeams = computed(() =>
  props.season.groups.some(group => group.participants.length > 0),
)

watch(
  () => props.season,
  season => {
    const next: Record<string, GroupName | null> = Object.fromEntries(
      season.availableClasses.map(code => [code, null]),
    )
    for (const group of season.groups) {
      for (const participant of group.participants) next[participant.classCode] = group.name
    }
    assignments.value = next
    editorPanel.value = hasSavedTeams.value ? undefined : 'editor'
    activeGroup.value =
      groupNames.find(group => classesIn(group).length < 6) ?? groupNames[groupNames.length - 1]
  },
  { immediate: true, deep: true },
)

function classesIn(group: GroupName) {
  return props.season.availableClasses.filter(code => assignments.value[code] === group)
}

function displayClass(code: string) {
  return `${code[0]}.${code[1].toLowerCase()}`
}

function selectClass(group: GroupName, code: string) {
  const current = assignments.value[code]
  if (current === group) {
    assignments.value[code] = null
    return
  }
  if (current || classesIn(group).length >= 6) return

  assignments.value[code] = group
  if (classesIn(group).length === 6) {
    const next = groupNames[groupNames.indexOf(group) + 1]
    if (next) activeGroup.value = next
  }
}

function isUnavailable(group: GroupName, code: string) {
  const assignedGroup = assignments.value[code]
  return Boolean(assignedGroup && assignedGroup !== group)
}

async function save() {
  loading.value = true
  try {
    await sportsStore.saveGroups(props.sport, {
      A: classesIn('A'),
      B: classesIn('B'),
      C: classesIn('C'),
      D: classesIn('D'),
    })
    editorPanel.value = undefined
    displaySnackbar('Razporeditev skupin je shranjena')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Skupin ni bilo mogoče shraniti')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-expansion-panels v-model="editorPanel" class="sports-group-editor my-4">
    <v-expansion-panel value="editor">
      <v-expansion-panel-title>
        <div>
          <strong>Uredi prijavljene ekipe in skupine</strong>
          <div class="text-caption opacity-70">
            {{ Object.values(assignments).filter(Boolean).length }} prijavljenih ekip
          </div>
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <p class="mb-4 opacity-70">
          Za vsako skupino izberite največ šest razredov. Neizbrani razredi ne sodelujejo.
        </p>

        <v-expansion-panels v-model="activeGroup" variant="accordion">
          <v-expansion-panel v-for="group in groupNames" :key="group" :value="group">
            <v-expansion-panel-title>
              <strong>Skupina {{ group }}</strong>
              <span class="ml-2 text-caption opacity-70">{{ classesIn(group).length }}/6</span>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="sports-team-pills">
                <v-btn
                  v-for="code in season.availableClasses"
                  :key="code"
                  rounded="pill"
                  size="small"
                  :variant="assignments[code] === group ? 'flat' : 'outlined'"
                  :color="assignments[code] === group ? 'secondary' : undefined"
                  :disabled="isUnavailable(group, code)"
                  :aria-pressed="assignments[code] === group"
                  @click="selectClass(group, code)"
                >
                  {{ displayClass(code) }}
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <v-btn
          :prepend-icon="mdiContentSave"
          text="Shrani skupine"
          color="secondary"
          class="mt-4"
          :loading="loading"
          @click="save"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<style scoped>
.sports-team-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
