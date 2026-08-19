<script setup lang="ts">
import { mdiCalendarPlus, mdiChevronLeft, mdiChevronRight } from '@mdi/js'
import { computed, ref, watch } from 'vue'

import { type ScheduleMatch, sportNames, useSportsStore } from '@/stores/sports'
import { getCurrentDate, getISODate } from '@/utils/days'

const dialog = defineModel<boolean>()
const emit = defineEmits<{ create: [date: string] }>()
const sportsStore = useSportsStore()
const loading = ref(false)
const currentMonth = ref(new Date(getCurrentDate().getFullYear(), getCurrentDate().getMonth(), 1))
const selectedDate = ref(getISODate(getCurrentDate()))
const matches = ref<ScheduleMatch[]>([])
const weekdays = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned']

const monthTitle = computed(() =>
  new Intl.DateTimeFormat('sl', { month: 'long', year: 'numeric' }).format(currentMonth.value),
)

const calendarDays = computed(() => {
  const first = new Date(currentMonth.value)
  const mondayOffset = (first.getDay() + 6) % 7
  first.setDate(first.getDate() - mondayOffset)
  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(first)
    date.setDate(first.getDate() + index)
    return {
      date,
      iso: getISODate(date),
      currentMonth: date.getMonth() === currentMonth.value.getMonth(),
    }
  })
})

const matchesByDate = computed(() => {
  const grouped = new Map<string, ScheduleMatch[]>()
  for (const match of matches.value) {
    if (!match.date) continue
    const dayMatches = grouped.get(match.date) || []
    dayMatches.push(match)
    grouped.set(match.date, dayMatches)
  }
  return grouped
})

const selectedMatches = computed(() => matchesByDate.value.get(selectedDate.value) || [])

function result(match: ScheduleMatch) {
  if (match.status === 'postponed') return 'preloženo'
  if (match.homeScore === null || match.awayScore === null) return '10:30'
  const penalties =
    match.homePenalties !== null && match.awayPenalties !== null
      ? ` (${match.homePenalties}:${match.awayPenalties} po kazenskih strelih)`
      : ''
  return `${match.homeScore}:${match.awayScore}${penalties}`
}

function matchLabel(match: ScheduleMatch) {
  return `${sportNames[match.sport]}: ${match.homeName} – ${match.awayName}, ${result(match)}`
}

function tooltip(date: string) {
  const dayMatches = matchesByDate.value.get(date)
  return dayMatches?.length ? dayMatches.map(matchLabel).join('\n') : 'Ni športnih tekem'
}

async function loadMonth() {
  loading.value = true
  try {
    const anchors = calendarDays.value.filter((_, index) => index % 7 === 0).map(day => day.iso)
    matches.value = await sportsStore.getScheduleWeeks(anchors)
  } finally {
    loading.value = false
  }
}

function moveMonth(offset: number) {
  currentMonth.value = new Date(
    currentMonth.value.getFullYear(),
    currentMonth.value.getMonth() + offset,
    1,
  )
  selectedDate.value = getISODate(currentMonth.value)
}

function createMatch() {
  emit('create', selectedDate.value)
  dialog.value = false
}

watch(dialog, open => {
  if (open) void loadMonth()
})

watch(currentMonth, () => {
  if (dialog.value) void loadMonth()
})
</script>

<template>
  <v-dialog v-model="dialog" max-width="620">
    <v-card title="Koledar tekem">
      <v-card-text>
        <div class="calendar-heading">
          <v-btn
            :icon="mdiChevronLeft"
            title="Prejšnji mesec"
            variant="text"
            @click="moveMonth(-1)"
          />
          <strong class="text-capitalize">{{ monthTitle }}</strong>
          <v-btn
            :icon="mdiChevronRight"
            title="Naslednji mesec"
            variant="text"
            @click="moveMonth(1)"
          />
        </div>

        <v-progress-linear v-if="loading" indeterminate color="secondary" class="mb-2" />
        <div class="sports-calendar">
          <div v-for="weekday in weekdays" :key="weekday" class="calendar-weekday">
            {{ weekday }}
          </div>
          <v-tooltip
            v-for="day in calendarDays"
            :key="day.iso"
            :text="tooltip(day.iso)"
            location="top"
          >
            <template #activator="{ props: tooltipProps }">
              <v-btn
                v-bind="tooltipProps"
                :aria-label="`${day.date.toLocaleDateString('sl')}: ${tooltip(day.iso)}`"
                :class="{ 'outside-month': !day.currentMonth }"
                :color="matchesByDate.has(day.iso) ? 'secondary' : 'surface-variant'"
                :variant="selectedDate === day.iso ? 'flat' : 'tonal'"
                class="calendar-day"
                @click="selectedDate = day.iso"
              >
                {{ day.date.getDate() }}
              </v-btn>
            </template>
          </v-tooltip>
        </div>

        <v-sheet border rounded class="pa-3 mt-4">
          <strong>{{ new Date(`${selectedDate}T12:00:00`).toLocaleDateString('sl') }}</strong>
          <v-list v-if="selectedMatches.length" density="compact" class="pa-0 mt-1">
            <v-list-item
              v-for="match in selectedMatches"
              :key="`${match.sport}-${match.id}`"
              :title="`${match.homeName} – ${match.awayName}`"
              :subtitle="`${sportNames[match.sport]} · ${result(match)}`"
            />
          </v-list>
          <p v-else class="mt-2 opacity-60">Ni športnih tekem.</p>
          <v-btn
            :prepend-icon="mdiCalendarPlus"
            text="Razporedi tekmo na izbrani dan"
            color="secondary"
            class="mt-3"
            @click="createMatch"
          />
        </v-sheet>
      </v-card-text>
      <v-card-actions><v-spacer /><v-btn text="Zapri" @click="dialog = false" /></v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style scoped>
.calendar-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.sports-calendar {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.35rem;
}

.calendar-weekday {
  padding-block: 0.25rem;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
}

.calendar-day {
  width: 100%;
  min-width: 0;
  height: 2.75rem;
  padding: 0;
}

.outside-month {
  opacity: 0.35;
}
</style>
