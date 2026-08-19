<script setup lang="ts">
import { computed, ref } from 'vue'

import type { GroupName, SportSlug, SportsMatch, SportsSeason, StandingRow } from '@/stores/sports'

const props = defineProps<{ sport: SportSlug; season: SportsSeason }>()
const selectedTeam = ref<StandingRow | null>(null)
const selectedGroup = ref<GroupName | null>(null)

type StatColumn = { key: keyof StandingRow; short: string; label: string }

const columns = computed<StatColumn[]>(() => {
  if (props.sport === 'football') {
    return [
      { key: 'played', short: 'T', label: 'Tekme' },
      { key: 'won', short: 'Z', label: 'Zmage' },
      { key: 'drawn', short: 'N', label: 'Neodločeno' },
      { key: 'lost', short: 'P', label: 'Porazi' },
      { key: 'scored', short: 'DZ', label: 'Dani zadetki' },
      { key: 'conceded', short: 'PZ', label: 'Prejeti zadetki' },
      { key: 'difference', short: 'RZ', label: 'Razlika zadetkov' },
      { key: 'points', short: 'PT', label: 'Točke' },
    ]
  }
  if (props.sport === 'basketball') {
    return [
      { key: 'played', short: 'T', label: 'Tekme' },
      { key: 'won', short: 'Z', label: 'Zmage' },
      { key: 'lost', short: 'P', label: 'Porazi' },
      { key: 'scored', short: 'DK', label: 'Dani koši' },
      { key: 'conceded', short: 'PK', label: 'Prejeti koši' },
      { key: 'difference', short: 'RK', label: 'Razlika košev' },
      { key: 'points', short: 'TČ', label: 'Točke' },
    ]
  }
  return [
    { key: 'played', short: 'T', label: 'Tekme' },
    { key: 'won', short: 'Z', label: 'Zmage' },
    { key: 'lost', short: 'P', label: 'Porazi' },
    { key: 'setsWon', short: 'DS', label: 'Dobljeni seti' },
    { key: 'setsLost', short: 'ZS', label: 'Izgubljeni seti' },
    { key: 'points', short: 'TČ', label: 'Točke' },
  ]
})

const selectedGroupData = computed(() =>
  props.season.groups.find(group => group.name === selectedGroup.value),
)

const teamStats = computed(() => {
  if (!selectedTeam.value) return []
  return columns.value.map(column => ({
    name: column.label,
    value: Number(selectedTeam.value?.[column.key] ?? 0),
  }))
})

function value(row: StandingRow, key: keyof StandingRow) {
  return row[key] ?? 0
}

function standingRowStyle(index: number, teamCount: number) {
  const remainingTeams = teamCount - 2
  const monochrome =
    index < 2 || remainingTeams <= 1 ? 0 : 0.1 * (1 - (index - 2) / (remainingTeams - 1))
  return { '--standing-monochrome': monochrome.toFixed(3) }
}

function matchResult(match: SportsMatch) {
  if (match.status === 'scheduled') return match.date ? 'Ob 10:30' : 'Ni razporejena'
  if (match.status === 'postponed') return 'Preloženo'
  const base = `${match.homeScore}:${match.awayScore}`
  const penalties =
    match.homePenalties !== null && match.awayPenalties !== null
      ? ` (${match.homePenalties}:${match.awayPenalties} po kazenskih strelih)`
      : ''
  return base + penalties + (match.status === 'forfeited' ? ' – predaja' : '')
}

function localizedDate(date: string | null) {
  return date ? new Date(`${date}T12:00:00`).toLocaleDateString('sl') : ''
}
</script>

<template>
  <v-row class="v-row--medium">
    <v-col v-for="group in season.groups" :key="group.name" cols="12" xl="6">
      <v-card-main>
        <template #title>
          <v-btn variant="text" class="sports-group-title px-0" @click="selectedGroup = group.name">
            Skupina {{ group.name }}
          </v-btn>
        </template>
        <template #text>
          <v-table density="compact" class="sports-table" aria-label="Lestvica skupine">
            <thead>
              <tr>
                <th>Mesto</th>
                <th>Razred</th>
                <th>Točke</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in group.standings"
                :key="row.classCode"
                tabindex="0"
                role="button"
                :aria-label="`Odpri statistiko za ${row.className}`"
                class="sports-ranked-row"
                :class="{ 'sports-advancing-row': index < 2 }"
                :style="standingRowStyle(index, group.standings.length)"
                @click="selectedTeam = row"
                @keydown.enter="selectedTeam = row"
                @keydown.space.prevent="selectedTeam = row"
              >
                <td>{{ row.rank }}</td>
                <th scope="row">{{ row.className }}</th>
                <td>{{ row.points }}</td>
              </tr>
              <tr v-if="!group.standings.length">
                <td colspan="3" class="py-5 opacity-60">Skupina je še prazna.</td>
              </tr>
            </tbody>
          </v-table>

          <div v-if="group.matches.length" class="mt-4">
            <strong>Tekme</strong>
            <v-list density="compact" class="pa-0 mt-1">
              <v-list-item
                v-for="match in group.matches"
                :key="match.id"
                :title="`${match.homeName} : ${match.awayName}`"
                :subtitle="`${localizedDate(match.date)} · ${matchResult(match)}`"
              />
            </v-list>
          </div>
        </template>
      </v-card-main>
    </v-col>
  </v-row>

  <v-dialog
    :model-value="Boolean(selectedTeam)"
    max-width="480"
    @update:model-value="selectedTeam = null"
  >
    <v-card :title="selectedTeam ? `Statistika – ${selectedTeam.className}` : 'Statistika'">
      <v-card-text>
        <v-table density="compact" class="sports-table">
          <thead>
            <tr>
              <th>Statistika</th>
              <th>Vrednost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stat in teamStats" :key="stat.name">
              <th scope="row">{{ stat.name }}</th>
              <td>{{ stat.value }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
      <v-card-actions
        ><v-spacer /><v-btn text="Zapri" @click="selectedTeam = null"
      /></v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog
    :model-value="Boolean(selectedGroupData)"
    width="calc(100% - 16px)"
    max-width="900"
    @update:model-value="selectedGroup = null"
  >
    <v-card :title="selectedGroup ? `Statistika skupine ${selectedGroup}` : 'Statistika skupine'">
      <v-card-text>
        <div class="sports-full-table">
          <v-table density="compact" class="sports-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Razred</th>
                <th v-for="column in columns" :key="column.key" :title="column.label">
                  {{ column.short }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, index) in selectedGroupData?.standings ?? []"
                :key="row.classCode"
                class="sports-ranked-row"
                :class="{ 'sports-advancing-row': index < 2 }"
                :style="standingRowStyle(index, selectedGroupData?.standings.length ?? 0)"
              >
                <td>{{ row.rank }}</td>
                <th scope="row">{{ row.className }}</th>
                <td v-for="column in columns" :key="column.key">{{ value(row, column.key) }}</td>
              </tr>
            </tbody>
          </v-table>
        </div>
        <div class="sports-stats-legend" aria-label="Legenda statistike">
          <strong>Legenda:</strong>
          <span v-for="column in columns" :key="column.key">
            <b>{{ column.short }}</b> – {{ column.label }}
          </span>
        </div>
      </v-card-text>
      <v-card-actions
        ><v-spacer /><v-btn text="Zapri" @click="selectedGroup = null"
      /></v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.sports-table {
  border: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 4px;
}

.sports-table tbody tr[role='button'] {
  cursor: pointer;
}

.sports-table tbody tr:nth-child(even):not(.sports-ranked-row) {
  background: rgba(var(--v-theme-on-surface), 0.055);
}

.sports-table tbody tr.sports-ranked-row {
  background: rgba(var(--v-theme-on-surface), var(--standing-monochrome));
}

.sports-table tbody tr.sports-advancing-row {
  background: rgba(var(--v-theme-secondary), 0.2);
}

.sports-table tbody tr[role='button']:hover,
.sports-table tbody tr[role='button']:focus-visible {
  background: rgba(var(--v-theme-secondary), 0.16);
  outline: none;
}

.sports-group-title {
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: normal;
  text-transform: none;
}

.sports-full-table {
  overflow-x: visible;
}

.sports-full-table .sports-table :deep(table) {
  width: 100%;
  table-layout: fixed;
}

.sports-full-table .sports-table :deep(th),
.sports-full-table .sports-table :deep(td) {
  min-width: 0;
  padding-right: 0.2rem !important;
  padding-left: 0.2rem !important;
  text-align: center;
  white-space: nowrap;
}

.sports-full-table .sports-table :deep(th:first-child),
.sports-full-table .sports-table :deep(td:first-child) {
  width: 7%;
}

.sports-full-table .sports-table :deep(th:nth-child(2)),
.sports-full-table .sports-table :deep(td:nth-child(2)) {
  width: 17%;
}

.sports-full-table .sports-table :deep(th + th),
.sports-full-table .sports-table :deep(td + td) {
  border-left: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.sports-stats-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 1rem;
  margin-top: 1rem;
  color: rgba(var(--v-theme-on-surface), 0.75);
  font-size: 0.78rem;
}

@media (max-width: 600px) {
  .sports-full-table .sports-table {
    font-size: 0.72rem;
  }

  .sports-full-table .sports-table :deep(th),
  .sports-full-table .sports-table :deep(td) {
    height: 34px;
    padding-right: 0.08rem !important;
    padding-left: 0.08rem !important;
  }
}
</style>
