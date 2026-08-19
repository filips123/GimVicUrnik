<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { useSnackbarStore } from '@/composables/snackbar'
import {
  type GroupName,
  type MatchStatus,
  sportNames,
  type SportSlug,
  type SportsMatch,
  useSportsStore,
} from '@/stores/sports'
import { getCurrentDate, getISODate } from '@/utils/days'

const dialog = defineModel<boolean>()
const props = defineProps<{ sport: SportSlug; match?: SportsMatch | null; initialDate?: string }>()
const emit = defineEmits<{ saved: [] }>()

const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const loading = ref(false)
const selectedGroup = ref<GroupName>('A')
const homeClass = ref<string | null>(null)
const awayClass = ref<string | null>(null)
const selectedMatchId = ref<number | null>(null)
const date = ref('')
const status = ref<MatchStatus>('scheduled')
const notes = ref('')
const homeScore = ref<number | null>(null)
const awayScore = ref<number | null>(null)
const homePenalties = ref<number | null>(null)
const awayPenalties = ref<number | null>(null)
const forfeitWinner = ref<string | null>(null)

const season = computed(() => sportsStore.seasons[props.sport])
const isNew = computed(() => !props.match)
const knockoutMode = computed(() => season.value?.phase === 'knockout')
const group = computed(() => season.value?.groups.find(item => item.name === selectedGroup.value))
const participantItems = computed(() =>
  (group.value?.participants || []).map(item => ({ title: item.className, value: item.classCode })),
)
const bracketChoices = computed(() =>
  (season.value?.bracket || [])
    .filter(match => match.homeClass && match.awayClass)
    .map(match => ({
      title: `${stageName(match.stage)}: ${match.homeName} – ${match.awayName}${match.date ? ` (${localizedDate(match.date)})` : ''}`,
      value: match.id,
    })),
)
const selectedBracketMatch = computed(() =>
  season.value?.bracket.find(match => match.id === selectedMatchId.value),
)
const targetMatch = computed(() => props.match || selectedBracketMatch.value || null)

function stageName(stage: SportsMatch['stage']) {
  return {
    group: 'Skupina',
    quarterfinal: 'Četrtfinale',
    semifinal: 'Polfinale',
    third_place: 'Za 3. mesto',
    final: 'Finale',
  }[stage]
}

function localizedDate(value: string) {
  return new Date(`${value}T12:00:00`).toLocaleDateString('sl')
}

function resetTeams() {
  homeClass.value = null
  awayClass.value = null
}

function resetFromMatch(match: SportsMatch | null | undefined) {
  selectedMatchId.value = match?.id || null
  selectedGroup.value = match?.group || 'A'
  homeClass.value = match?.homeClass || null
  awayClass.value = match?.awayClass || null
  date.value = match?.date || props.initialDate || getISODate(getCurrentDate())
  status.value = match?.status || 'scheduled'
  notes.value = match?.notes || ''
  homeScore.value = match?.homeScore ?? null
  awayScore.value = match?.awayScore ?? null
  homePenalties.value = match?.homePenalties ?? null
  awayPenalties.value = match?.awayPenalties ?? null
  forfeitWinner.value = match?.forfeitWinner || null
}

watch(dialog, open => {
  if (open) resetFromMatch(props.match)
})

watch(selectedMatchId, id => {
  if (isNew.value && knockoutMode.value && id) resetFromMatch(selectedBracketMatch.value)
})

function resultPayload() {
  const value: Record<string, any> = { date: date.value, status: status.value, notes: notes.value }
  if (status.value === 'forfeited') value.forfeitWinner = forfeitWinner.value
  if (status.value !== 'completed') return value
  value.homeScore = homeScore.value
  value.awayScore = awayScore.value
  if (props.sport === 'football' && targetMatch.value?.stage !== 'group') {
    value.homePenalties = homePenalties.value
    value.awayPenalties = awayPenalties.value
  }
  return value
}

async function save(confirmWarnings = false) {
  loading.value = true
  try {
    let result: { warnings?: string[] }
    if (isNew.value && !knockoutMode.value) {
      result = await sportsStore.createMatch(props.sport, {
        homeClass: homeClass.value,
        awayClass: awayClass.value,
        date: date.value,
        notes: notes.value,
        confirmWarnings,
      })
    } else {
      if (!targetMatch.value) throw new Error('Izberite tekmo.')
      result = await sportsStore.updateMatch(props.sport, targetMatch.value, {
        ...resultPayload(),
        confirmWarnings,
      })
    }
    if (result.warnings?.length) {
      loading.value = false
      if (window.confirm(`${result.warnings.join('\n')}\n\nŽelite tekmo vseeno shraniti?`)) {
        await save(true)
      }
      return
    }
    dialog.value = false
    displaySnackbar('Tekma je shranjena')
    emit('saved')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Tekme ni bilo mogoče shraniti')
  } finally {
    loading.value = false
  }
}

async function remove() {
  if (!props.match || !window.confirm('Želite odstraniti to neodigrano tekmo?')) return
  loading.value = true
  try {
    await sportsStore.deleteMatch(props.sport, props.match)
    dialog.value = false
    displaySnackbar('Tekma je odstranjena')
    emit('saved')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Tekme ni bilo mogoče odstraniti')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-dialog v-model="dialog">
    <v-card :title="`${isNew ? 'Nova tekma' : 'Uredi tekmo'} – ${sportNames[sport]}`">
      <template #text>
        <template v-if="isNew && knockoutMode">
          <v-select
            v-model="selectedMatchId"
            label="Tekma izločilnih bojev"
            :items="bracketChoices"
          />
        </template>
        <template v-else-if="isNew">
          <v-select
            v-model="selectedGroup"
            label="Skupina"
            :items="['A', 'B', 'C', 'D']"
            @update:model-value="resetTeams"
          />
          <v-row>
            <v-col cols="12" sm="6">
              <v-select v-model="homeClass" label="Prva ekipa" :items="participantItems" />
            </v-col>
            <v-col cols="12" sm="6">
              <v-select v-model="awayClass" label="Druga ekipa" :items="participantItems" />
            </v-col>
          </v-row>
        </template>

        <v-alert v-if="targetMatch" type="info" variant="tonal" class="mb-4">
          {{ targetMatch.homeName }} – {{ targetMatch.awayName }} ·
          {{ stageName(targetMatch.stage) }}
        </v-alert>

        <v-text-field v-model="date" type="date" label="Datum" />
        <v-text-field model-value="10:30" label="Začetek" disabled />

        <v-select
          v-if="!isNew || knockoutMode"
          v-model="status"
          label="Stanje"
          :items="[
            { title: 'Razporejena', value: 'scheduled' },
            { title: 'Preložena', value: 'postponed' },
            { title: 'Odigrana', value: 'completed' },
            { title: 'Predana', value: 'forfeited' },
          ]"
        />

        <template v-if="status === 'completed'">
          <v-row>
            <v-col cols="6"
              ><v-text-field
                v-model.number="homeScore"
                type="number"
                min="0"
                :max="sport === 'volleyball' ? 2 : undefined"
                :label="sport === 'volleyball' ? 'Seti prve ekipe' : 'Rezultat prve ekipe'"
            /></v-col>
            <v-col cols="6"
              ><v-text-field
                v-model.number="awayScore"
                type="number"
                min="0"
                :max="sport === 'volleyball' ? 2 : undefined"
                :label="sport === 'volleyball' ? 'Seti druge ekipe' : 'Rezultat druge ekipe'"
            /></v-col>
          </v-row>
          <v-row
            v-if="sport === 'football' && targetMatch?.stage !== 'group' && homeScore === awayScore"
          >
            <v-col cols="6"
              ><v-text-field
                v-model.number="homePenalties"
                type="number"
                min="0"
                label="Kazenski streli – prva"
            /></v-col>
            <v-col cols="6"
              ><v-text-field
                v-model.number="awayPenalties"
                type="number"
                min="0"
                label="Kazenski streli – druga"
            /></v-col>
          </v-row>
        </template>

        <v-select
          v-if="status === 'forfeited'"
          v-model="forfeitWinner"
          label="Zmagovalec zaradi predaje"
          :items="[
            { title: targetMatch?.homeName || '', value: targetMatch?.homeClass },
            { title: targetMatch?.awayName || '', value: targetMatch?.awayClass },
          ]"
        />
        <v-textarea v-model="notes" label="Opomba (neobvezno)" rows="2" />
      </template>
      <template #actions>
        <v-btn
          v-if="match?.stage === 'group' && ['scheduled', 'postponed'].includes(match.status)"
          text="Odstrani"
          color="error"
          @click="remove"
        />
        <v-spacer />
        <v-btn text="Prekliči" @click="dialog = false" />
        <v-btn
          text="Shrani"
          :loading="loading"
          :disabled="isNew && knockoutMode ? !selectedMatchId : isNew && (!homeClass || !awayClass)"
          @click="save()"
        />
      </template>
    </v-card>
  </v-dialog>
</template>
