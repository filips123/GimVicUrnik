<script setup lang="ts">
import { mdiArrowDown, mdiArrowUp, mdiLock, mdiLockOpen } from '@mdi/js'
import { computed, defineAsyncComponent, ref, watch } from 'vue'

import SportsBracket from '@/components/SportsBracket.vue'
import SportsRules from '@/components/SportsRules.vue'
import SportsStandings from '@/components/SportsStandings.vue'
import { useSnackbarStore } from '@/composables/snackbar'
import type { GroupName, QualificationTie, SportSlug, SportsSeason } from '@/stores/sports'
import { useSportsStore } from '@/stores/sports'

const SportsGroupEditor = defineAsyncComponent(() => import('@/components/SportsGroupEditor.vue'))

const props = defineProps<{ sport: SportSlug; season: SportsSeason; editable: boolean }>()
const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const view = ref<'groups' | 'bracket'>('groups')
const tieDialog = ref(false)
const loading = ref(false)
const decisions = ref<Record<string, { orderedClasses: string[]; reason: string }>>({})

const hasTeams = computed(() => props.season.groups.some(group => group.participants.length))
const unresolvedTies = computed(() => props.season.qualificationTies.filter(tie => !tie.resolved))
const bracketAvailable = computed(() => ['knockout', 'completed'].includes(props.season.phase))

watch(
  () => props.season.phase,
  phase => {
    view.value = ['knockout', 'completed'].includes(phase) ? 'bracket' : 'groups'
  },
  { immediate: true },
)

function prepareTies() {
  decisions.value = Object.fromEntries(
    unresolvedTies.value.map(tie => [
      tie.group,
      { orderedClasses: [...tie.classCodes], reason: '' },
    ]),
  )
}

async function requestClose() {
  if (unresolvedTies.value.length) {
    prepareTies()
    tieDialog.value = true
    return
  }
  await closeGroups([])
}

async function closeGroups(
  tieDecisions: { group: GroupName; orderedClasses: string[]; reason: string }[],
) {
  loading.value = true
  try {
    await sportsStore.closeGroupStage(props.sport, tieDecisions)
    tieDialog.value = false
    view.value = 'bracket'
    displaySnackbar('Skupinski del je zaključen')
  } catch (error) {
    displaySnackbar(
      error instanceof Error ? error.message : 'Skupinskega dela ni bilo mogoče zaključiti',
    )
  } finally {
    loading.value = false
  }
}

async function submitTies() {
  const values = unresolvedTies.value.map(tie => ({
    group: tie.group,
    ...decisions.value[tie.group],
  }))
  await closeGroups(values)
}

function move(tie: QualificationTie, index: number, direction: number) {
  const order = decisions.value[tie.group].orderedClasses
  const target = index + direction
  if (target < 0 || target >= order.length) return
  ;[order[index], order[target]] = [order[target], order[index]]
}

function className(code: string) {
  return `${code[0]}.${code[1].toLowerCase()}`
}

async function reopenGroups() {
  if (
    !window.confirm(
      'Ponovno odprtje skupinskega dela bo odstranilo vse pare, termine in rezultate izločilnih bojev. Nadaljujem?',
    )
  ) {
    return
  }
  loading.value = true
  try {
    await sportsStore.reopenGroupStage(props.sport)
    view.value = 'groups'
    displaySnackbar('Skupinski del je ponovno odprt')
  } catch (error) {
    displaySnackbar(
      error instanceof Error ? error.message : 'Skupinskega dela ni bilo mogoče odpreti',
    )
  } finally {
    loading.value = false
  }
}

async function completeSeason() {
  if (!window.confirm('Želite zaključiti sezono in jo zakleniti?')) return
  loading.value = true
  try {
    await sportsStore.completeSeason(props.sport)
    displaySnackbar('Sezona je zaključena')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Sezone ni bilo mogoče zaključiti')
  } finally {
    loading.value = false
  }
}

async function reopenSeason() {
  loading.value = true
  try {
    await sportsStore.reopenSeason(props.sport)
    displaySnackbar('Sezona je ponovno odprta')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Sezone ni bilo mogoče odpreti')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-alert v-if="season.phase === 'completed'" type="success" variant="tonal" class="mb-4">
    Tekmovanje je zaključeno.
  </v-alert>

  <v-tabs v-if="bracketAvailable" v-model="view" grow class="mb-4">
    <v-tab value="groups" text="Skupinski del" />
    <v-tab value="bracket" text="Izločilni boji" />
  </v-tabs>

  <v-window v-model="view" :touch="false">
    <v-window-item value="groups">
      <v-alert v-if="!hasTeams && !editable" type="info" variant="tonal" class="mb-4">
        Ekipe in skupine še niso objavljene.
      </v-alert>

      <SportsStandings v-if="hasTeams" :sport="sport" :season="season" />

      <v-alert
        v-for="decision in season.qualificationDecisions"
        :key="decision.group"
        type="info"
        variant="tonal"
        class="my-3"
      >
        Skupina {{ decision.group }}: vrstni red izenačenih ekip je določil organizator.
        {{ decision.reason }}
      </v-alert>

      <SportsGroupEditor
        v-if="editable && ['setup', 'group_stage'].includes(season.phase)"
        :sport="sport"
        :season="season"
      />

      <div v-if="editable" class="d-flex flex-wrap ga-2 my-4">
        <v-btn
          v-if="['setup', 'group_stage'].includes(season.phase)"
          :prepend-icon="mdiLock"
          text="Zaključi skupinski del"
          color="secondary"
          :loading="loading"
          @click="requestClose"
        />
        <v-btn
          v-else-if="season.phase === 'knockout'"
          :prepend-icon="mdiLockOpen"
          text="Ponovno odpri skupinski del"
          variant="outlined"
          color="secondary"
          :loading="loading"
          @click="reopenGroups"
        />
      </div>
    </v-window-item>

    <v-window-item value="bracket">
      <SportsBracket
        :sport="sport"
        :season="season"
        :editable="editable && season.phase === 'knockout'"
      />
      <div v-if="editable" class="d-flex flex-wrap ga-2 my-4">
        <v-btn
          v-if="season.phase === 'knockout'"
          text="Zaključi sezono"
          color="secondary"
          :loading="loading"
          @click="completeSeason"
        />
        <v-btn
          v-if="season.phase === 'completed'"
          text="Ponovno odpri sezono"
          variant="outlined"
          color="secondary"
          :loading="loading"
          @click="reopenSeason"
        />
      </div>
    </v-window-item>
  </v-window>

  <SportsRules
    :sport="sport"
    :rules="season.rules"
    :editable="editable && season.phase !== 'completed'"
  />

  <v-dialog v-model="tieDialog">
    <v-card title="Razreši izenačenja">
      <template #text>
        <p class="mb-4">Razvrstite izenačene ekipe. Višje uvrščene ekipe bodo imele prednost.</p>
        <v-card
          v-for="tie in unresolvedTies"
          :key="tie.group"
          :title="`Skupina ${tie.group}`"
          variant="outlined"
          class="mb-4"
        >
          <v-list>
            <v-list-item
              v-for="(code, index) in decisions[tie.group]?.orderedClasses"
              :key="code"
              :title="`${index + 1}. ${className(code)}`"
            >
              <template #append>
                <v-btn
                  :icon="mdiArrowUp"
                  title="Premakni navzgor"
                  variant="text"
                  @click="move(tie, index, -1)"
                />
                <v-btn
                  :icon="mdiArrowDown"
                  title="Premakni navzdol"
                  variant="text"
                  @click="move(tie, index, 1)"
                />
              </template>
            </v-list-item>
          </v-list>
          <v-card-text>
            <v-textarea v-model="decisions[tie.group].reason" label="Razlog odločitve" rows="2" />
          </v-card-text>
        </v-card>
      </template>
      <template #actions>
        <v-btn text="Prekliči" @click="tieDialog = false" />
        <v-btn
          text="Potrdi in zaključi"
          :loading="loading"
          :disabled="unresolvedTies.some(tie => !decisions[tie.group]?.reason.trim())"
          @click="submitTies"
        />
      </template>
    </v-card>
  </v-dialog>
</template>
