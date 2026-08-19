<script setup lang="ts">
import { mdiTrophy } from '@mdi/js'
import { computed, ref, watch } from 'vue'
import { useDisplay } from 'vuetify'

import { useSnackbarStore } from '@/composables/snackbar'
import type { SportSlug, SportsMatch, SportsSeason } from '@/stores/sports'
import { useSportsStore } from '@/stores/sports'

const props = defineProps<{ sport: SportSlug; season: SportsSeason; editable: boolean }>()
const sportsStore = useSportsStore()
const { displaySnackbar } = useSnackbarStore()
const { mobile, height } = useDisplay()
const quarterfinalNames = ['QF1', 'QF2', 'QF3', 'QF4'] as const
const bracketSlotOrder = ['QF1', 'QF2', 'QF3', 'QF4', 'SF1', 'SF2', 'FINAL', 'THIRD']
const loading = ref(false)
const editorPanel = ref<string | undefined>()
const activeQuarterfinal = ref<(typeof quarterfinalNames)[number]>('QF1')
const slots = ref<Record<string, string[]>>({ QF1: [], QF2: [], QF3: [], QF4: [] })

const qualifiers = computed(() =>
  props.season.groups
    .flatMap(group => group.participants)
    .filter(participant => participant.qualifiedRank)
    .sort((left, right) => left.classCode.localeCompare(right.classCode)),
)
const bracketCreated = computed(() => props.season.bracket.length > 0)
const playedKnockout = computed(() =>
  props.season.bracket.some(match => ['completed', 'forfeited'].includes(match.status)),
)
const usedTeams = computed(() => new Set(Object.values(slots.value).flat()))
const allQuarterfinalsReady = computed(
  () =>
    quarterfinalNames.every(slot => slots.value[slot].length === 2) && usedTeams.value.size === 8,
)
const bracketScale = computed(() => {
  if (!mobile.value) return 1.5

  // Fill the usable vertical space between the tournament header and mobile navigation.
  return Math.max(0.9, Math.min((height.value - 420) / 360, 1.45))
})
const bracketStageStyle = computed(() => ({
  width: `${655 * bracketScale.value}px`,
  height: `${360 * bracketScale.value}px`,
}))

watch(
  () => props.season.bracket,
  bracket => {
    slots.value = { QF1: [], QF2: [], QF3: [], QF4: [] }
    for (const match of bracket.filter(match => match.stage === 'quarterfinal')) {
      if (match.bracketSlot && match.homeClass && match.awayClass) {
        slots.value[match.bracketSlot] = [match.homeClass, match.awayClass]
      }
    }
    activeQuarterfinal.value =
      quarterfinalNames.find(slot => slots.value[slot].length < 2) ?? quarterfinalNames[3]
    editorPanel.value = bracket.length ? undefined : 'editor'
  },
  { immediate: true, deep: true },
)

function displayClass(code: string | null) {
  return code ? `${code[0]}.${code[1].toLowerCase()}` : 'Še ni znano'
}

function selectTeam(slot: (typeof quarterfinalNames)[number], code: string) {
  const pair = slots.value[slot]
  const selectedIndex = pair.indexOf(code)
  if (selectedIndex >= 0) {
    pair.splice(selectedIndex, 1)
    return
  }
  if (usedTeams.value.has(code) || pair.length >= 2) return

  pair.push(code)
  if (pair.length === 2) {
    const next = quarterfinalNames[quarterfinalNames.indexOf(slot) + 1]
    if (next) activeQuarterfinal.value = next
  }
}

function unavailable(slot: string, code: string) {
  return usedTeams.value.has(code) && !slots.value[slot].includes(code)
}

async function saveBracket() {
  loading.value = true
  try {
    await sportsStore.assignQuarterfinals(props.sport, slots.value)
    editorPanel.value = undefined
    displaySnackbar('Četrtfinalni pari so shranjeni')
  } catch (error) {
    displaySnackbar(error instanceof Error ? error.message : 'Parov ni bilo mogoče shraniti')
  } finally {
    loading.value = false
  }
}

function matches(stage: SportsMatch['stage']) {
  return props.season.bracket
    .filter(match => match.stage === stage)
    .sort(
      (left, right) =>
        bracketSlotOrder.indexOf(left.bracketSlot || '') -
        bracketSlotOrder.indexOf(right.bracketSlot || ''),
    )
}

const quarterfinalMatches = computed(() => matches('quarterfinal'))
const semifinalMatches = computed(() => matches('semifinal'))

function winner(match: SportsMatch, side: 'home' | 'away') {
  if (!['completed', 'forfeited'].includes(match.status)) return false
  if (
    match.homeScore === match.awayScore &&
    match.homePenalties !== null &&
    match.awayPenalties !== null
  ) {
    return side === 'home'
      ? match.homePenalties > match.awayPenalties
      : match.awayPenalties > match.homePenalties
  }
  return side === 'home'
    ? Number(match.homeScore) > Number(match.awayScore)
    : Number(match.awayScore) > Number(match.homeScore)
}

function dateLabel(match: SportsMatch) {
  return match.date
    ? new Date(`${match.date}T12:00:00`).toLocaleDateString('sl')
    : 'Datum še ni določen'
}

function scoreLabel(match: SportsMatch, side: 'home' | 'away') {
  const score = side === 'home' ? match.homeScore : match.awayScore
  const penalties = side === 'home' ? match.homePenalties : match.awayPenalties
  return penalties === null ? (score ?? '–') : `${score ?? '–'} (${penalties})`
}

function orderedTeams(match: SportsMatch) {
  const teams = (['home', 'away'] as const).map(side => ({
    side,
    classCode: side === 'home' ? match.homeClass : match.awayClass,
    winning: winner(match, side),
  }))
  return teams[1].winning ? [teams[1], teams[0]] : teams
}

function hasWinner(match: SportsMatch | undefined) {
  return Boolean(match && (winner(match, 'home') || winner(match, 'away')))
}

function slotLabel(match: SportsMatch) {
  if (match.bracketSlot?.startsWith('QF')) return match.bracketSlot.replace('QF', 'Četrtfinale ')
  if (match.bracketSlot?.startsWith('SF')) return match.bracketSlot.replace('SF', 'Polfinale ')
  if (match.bracketSlot === 'THIRD') return 'Za 3. mesto'
  return 'Finale'
}
</script>

<template>
  <v-sheet v-if="season.podium" border rounded class="sports-podium-wrap mb-4">
    <div class="sports-podium">
      <div class="podium-place podium-silver">
        <strong>{{ displayClass(season.podium.silver) }}</strong>
      </div>
      <div class="podium-place podium-gold">
        <v-icon :icon="mdiTrophy" size="small" />
        <strong>{{ displayClass(season.podium.gold) }}</strong>
      </div>
      <div class="podium-place podium-bronze">
        <strong>{{ displayClass(season.podium.bronze) }}</strong>
      </div>
    </div>
  </v-sheet>

  <v-expansion-panels v-if="editable && !playedKnockout" v-model="editorPanel" class="mb-5">
    <v-expansion-panel value="editor">
      <v-expansion-panel-title>
        <div>
          <strong>{{
            bracketCreated ? 'Uredi četrtfinalne pare' : 'Razporedi četrtfinale'
          }}</strong>
          <div class="text-caption opacity-70">{{ usedTeams.size }}/8 izbranih ekip</div>
        </div>
      </v-expansion-panel-title>
      <v-expansion-panel-text>
        <p class="mb-4 opacity-70">
          Izberite po dve ekipi. Po končanem paru se samodejno odpre naslednji.
        </p>
        <v-expansion-panels v-model="activeQuarterfinal" variant="accordion">
          <v-expansion-panel v-for="slot in quarterfinalNames" :key="slot" :value="slot">
            <v-expansion-panel-title>
              <strong>{{ slot.replace('QF', 'Četrtfinale ') }}</strong>
              <span class="ml-2 text-caption opacity-70">{{ slots[slot].length }}/2</span>
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <div class="sports-team-pills">
                <v-btn
                  v-for="team in qualifiers"
                  :key="team.classCode"
                  rounded="pill"
                  size="small"
                  :variant="slots[slot].includes(team.classCode) ? 'flat' : 'outlined'"
                  :color="slots[slot].includes(team.classCode) ? 'secondary' : undefined"
                  :disabled="unavailable(slot, team.classCode)"
                  :aria-pressed="slots[slot].includes(team.classCode)"
                  @click="selectTeam(slot, team.classCode)"
                >
                  {{ team.className }}
                </v-btn>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
        <v-btn
          text="Shrani četrtfinale"
          color="secondary"
          class="mt-4"
          :loading="loading"
          :disabled="!allQuarterfinalsReady"
          @click="saveBracket"
        />
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>

  <div v-if="bracketCreated" class="sports-bracket-scroll" aria-label="Izločilni boji">
    <div class="sports-bracket-stage" :style="bracketStageStyle">
      <div class="sports-bracket-canvas" :style="{ transform: `scale(${bracketScale})` }">
        <svg class="bracket-connectors" viewBox="0 0 655 360" aria-hidden="true">
          <path v-if="hasWinner(quarterfinalMatches[0])" d="M175 68 H208 V108" />
          <path v-if="hasWinner(quarterfinalMatches[1])" d="M175 148 H208 V108" />
          <path
            v-if="hasWinner(quarterfinalMatches[0]) && hasWinner(quarterfinalMatches[1])"
            d="M208 108 H240"
          />
          <path v-if="hasWinner(quarterfinalMatches[2])" d="M175 228 H208 V268" />
          <path v-if="hasWinner(quarterfinalMatches[3])" d="M175 308 H208 V268" />
          <path
            v-if="hasWinner(quarterfinalMatches[2]) && hasWinner(quarterfinalMatches[3])"
            d="M208 268 H240"
          />
          <path v-if="hasWinner(semifinalMatches[0])" d="M415 95 H448 V175" />
          <path v-if="hasWinner(semifinalMatches[1])" d="M415 255 H448 V175" />
          <path
            v-if="hasWinner(semifinalMatches[0]) && hasWinner(semifinalMatches[1])"
            d="M448 175 H480"
          />
        </svg>

        <section class="bracket-round bracket-quarterfinals">
          <article
            v-for="(match, index) in quarterfinalMatches"
            :key="match.id"
            class="bracket-match"
            :style="{ top: `${35 + index * 80}px` }"
          >
            <div class="match-meta">{{ slotLabel(match) }} · {{ dateLabel(match) }}</div>
            <div
              v-for="team in orderedTeams(match)"
              :key="team.side"
              class="team-row"
              :class="{ winner: team.winning }"
            >
              <span>{{ displayClass(team.classCode) }}</span>
              <strong>{{ scoreLabel(match, team.side) }}</strong>
            </div>
          </article>
        </section>

        <section class="bracket-round bracket-semifinals">
          <article
            v-for="(match, index) in semifinalMatches"
            :key="match.id"
            class="bracket-match"
            :style="{ top: `${62 + index * 160}px` }"
          >
            <div class="match-meta">{{ slotLabel(match) }} · {{ dateLabel(match) }}</div>
            <div
              v-for="team in orderedTeams(match)"
              :key="team.side"
              class="team-row"
              :class="{ winner: team.winning }"
            >
              <span>{{ displayClass(team.classCode) }}</span>
              <strong>{{ scoreLabel(match, team.side) }}</strong>
            </div>
          </article>
        </section>

        <section class="bracket-round bracket-finals">
          <article
            v-for="match in matches('final')"
            :key="match.id"
            class="bracket-match bracket-final"
          >
            <div class="match-meta">{{ slotLabel(match) }} · {{ dateLabel(match) }}</div>
            <div
              v-for="team in orderedTeams(match)"
              :key="team.side"
              class="team-row"
              :class="{ winner: team.winning }"
            >
              <span>{{ displayClass(team.classCode) }}</span>
              <strong>{{ scoreLabel(match, team.side) }}</strong>
            </div>
          </article>

          <article v-for="match in matches('third_place')" :key="match.id" class="bracket-match">
            <div class="match-meta">{{ slotLabel(match) }} · {{ dateLabel(match) }}</div>
            <div
              v-for="team in orderedTeams(match)"
              :key="team.side"
              class="team-row"
              :class="{ winner: team.winning }"
            >
              <span>{{ displayClass(team.classCode) }}</span>
              <strong>{{ scoreLabel(match, team.side) }}</strong>
            </div>
          </article>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sports-team-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.sports-bracket-scroll {
  overflow-x: auto;
  padding: 0.5rem 0 1.25rem;
  scroll-snap-type: x proximity;
}

.sports-bracket-canvas {
  position: relative;
  width: 655px;
  height: 360px;
  transform-origin: top left;
}

.bracket-round {
  position: absolute;
  top: 0;
  width: 175px;
  height: 360px;
}

.bracket-quarterfinals {
  left: 0;
}

.bracket-semifinals {
  left: 240px;
}

.bracket-finals {
  left: 480px;
}

.bracket-match {
  position: absolute;
  left: 0;
  z-index: 1;
  box-sizing: border-box;
  width: 175px;
  height: 74px;
  overflow: hidden;
  border: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 0.6rem;
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}

.bracket-connectors {
  position: absolute;
  inset: 0;
  width: 655px;
  height: 360px;
  overflow: visible;
  fill: none;
  stroke: rgba(var(--v-theme-secondary), 0.6);
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
}

.match-meta {
  box-sizing: border-box;
  height: 20px;
  overflow: hidden;
  padding: 0.1rem 0.45rem;
  border-bottom: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  color: rgba(var(--v-theme-on-surface), 0.65);
  font-size: 0.6rem;
  line-height: 17px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.team-row {
  display: flex;
  box-sizing: border-box;
  min-height: 26px;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
  padding: 0.1rem 0.45rem;
  font-size: 0.78rem;
  line-height: 20px;
}

.team-row span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.team-row strong {
  flex: 0 0 auto;
}

.team-row + .team-row {
  border-top: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.team-row.winner {
  border-left: 3px solid rgb(var(--v-theme-secondary));
  background: rgba(var(--v-theme-secondary), 0.1);
  font-weight: 700;
}

.bracket-final {
  top: 129px;
}

.bracket-finals .bracket-match:not(.bracket-final) {
  top: 250px;
}

.sports-podium-wrap {
  padding: 0.5rem 0.75rem 0;
}

.sports-podium {
  display: flex;
  align-items: end;
  justify-content: center;
  gap: 0.75rem;
  text-align: center;
}

.podium-place {
  position: relative;
  display: flex;
  min-width: 4.25rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem 0.5rem 0 0;
  padding: 0.35rem 0.5rem;
  color: #191919;
}

.podium-place strong {
  position: absolute;
  right: 0;
  bottom: 0.35rem;
  left: 0;
  text-align: center;
}

.podium-gold {
  min-height: 4.25rem;
  background: #ffd54f;
}
.podium-silver {
  min-height: 3.4rem;
  background: #cfd8dc;
}
.podium-bronze {
  min-height: 2.9rem;
  background: #cd7f32;
}

@media (max-width: 600px) {
  .sports-bracket-scroll {
    scroll-snap-type: x proximity;
  }
}
</style>
