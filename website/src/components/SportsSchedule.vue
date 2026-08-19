<script setup lang="ts">
import { mdiCalendarMonth, mdiCalendarPlus } from '@mdi/js'
import { storeToRefs } from 'pinia'
import { computed, defineAsyncComponent, ref } from 'vue'
import { useDisplay } from 'vuetify'

import { useSessionStore } from '@/stores/session'
import { type ScheduleMatch, sportNames, type SportSlug, useSportsStore } from '@/stores/sports'
import { getCurrentDate, getISODate } from '@/utils/days'
import { localizeDate, localizeDay } from '@/utils/localization'

const SportsMatchCalendar = defineAsyncComponent(
  () => import('@/components/SportsMatchCalendar.vue'),
)
const SportsMatchDialog = defineAsyncComponent(() => import('@/components/SportsMatchDialog.vue'))

const sportsStore = useSportsStore()
const { scheduleDays, scheduleWeekStart, admin, selectedSeasonKey } = storeToRefs(sportsStore)
const { day: activeDay } = storeToRefs(useSessionStore())
const { mobile } = useDisplay()
const dialog = ref(false)
const calendarDialog = ref(false)
const editingMatch = ref<ScheduleMatch | null>(null)
const editingSport = ref<SportSlug>('football')
const initialDate = ref(getISODate(getCurrentDate()))

const weekDates = computed(() => {
  if (!scheduleWeekStart.value) return []
  const monday = new Date(`${scheduleWeekStart.value}T12:00:00`)
  return Array.from({ length: 5 }, (_, index) => {
    const date = new Date(monday)
    date.setDate(monday.getDate() + index)
    return date
  })
})

function createMatch(dayIndex = activeDay.value) {
  if (!admin.value.authenticated || !admin.value.sport) return
  createMatchOnDate(getISODate(weekDates.value[dayIndex] || getCurrentDate()))
}

function createMatchOnDate(selectedDate: string) {
  if (!admin.value.authenticated || !admin.value.sport) return
  editingMatch.value = null
  editingSport.value = admin.value.sport
  initialDate.value = selectedDate
  dialog.value = true
}

function editMatch(match: ScheduleMatch) {
  if (
    !admin.value.authenticated ||
    admin.value.sport !== match.sport ||
    match.seasonKey !== selectedSeasonKey.value
  ) {
    return
  }
  editingMatch.value = match
  editingSport.value = match.sport
  initialDate.value = match.date || getISODate(getCurrentDate())
  dialog.value = true
}

function score(match: ScheduleMatch) {
  if (match.status === 'postponed') return 'Preloženo'
  if (match.homeScore === null || match.awayScore === null) return '10:30'
  const penalties =
    match.homePenalties !== null && match.awayPenalties !== null
      ? ` (${match.homePenalties}:${match.awayPenalties})`
      : ''
  return `${match.homeScore}:${match.awayScore}${penalties}${match.status === 'forfeited' ? ' · predaja' : ''}`
}

function editable(match: ScheduleMatch) {
  return (
    admin.value.authenticated &&
    admin.value.sport === match.sport &&
    match.seasonKey === selectedSeasonKey.value
  )
}
</script>

<template>
  <template v-if="mobile">
    <v-window v-model="activeDay" class="h-100">
      <v-window-item v-for="(matches, dayIndex) in scheduleDays" :key="dayIndex" :value="dayIndex">
        <v-card-main :subtitle="weekDates[dayIndex] ? localizeDate(weekDates[dayIndex]) : ''">
          <template #text>
            <v-list v-if="matches.length" class="pa-0">
              <v-list-item
                v-for="match in matches"
                :key="`${match.sport}-${match.id}`"
                :title="`${match.homeName} – ${match.awayName}`"
                :subtitle="`${sportNames[match.sport]} · ${score(match)}`"
                :class="{ 'sports-match-editable': editable(match) }"
                @click="editMatch(match)"
              />
            </v-list>
            <p v-else class="opacity-60">Ni športnih tekem.</p>
          </template>
        </v-card-main>
      </v-window-item>
    </v-window>
  </template>

  <v-row v-else class="v-row--medium">
    <v-col v-for="(matches, dayIndex) in scheduleDays" :key="dayIndex">
      <v-card-main
        :title="weekDates[dayIndex] ? localizeDay(weekDates[dayIndex]) : ''"
        :subtitle="weekDates[dayIndex] ? localizeDate(weekDates[dayIndex]) : ''"
        class="h-100"
      >
        <template #text>
          <v-list v-if="matches.length" class="pa-0">
            <v-list-item
              v-for="match in matches"
              :key="`${match.sport}-${match.id}`"
              :title="`${match.homeName} – ${match.awayName}`"
              :subtitle="`${sportNames[match.sport]} · ${score(match)}`"
              :class="{ 'sports-match-editable': editable(match) }"
              @click="editMatch(match)"
            />
          </v-list>
          <p v-else class="opacity-60">Ni športnih tekem.</p>
        </template>
      </v-card-main>
    </v-col>
  </v-row>

  <div v-if="admin.authenticated" class="d-flex flex-wrap ga-2 mt-4">
    <v-btn
      :prepend-icon="mdiCalendarPlus"
      text="Razporedi tekmo"
      color="secondary"
      @click="createMatch()"
    />
    <v-btn
      :icon="mobile ? mdiCalendarMonth : undefined"
      :prepend-icon="mobile ? undefined : mdiCalendarMonth"
      :text="mobile ? undefined : 'Koledar tekem'"
      aria-label="Koledar tekem"
      title="Koledar tekem"
      variant="outlined"
      color="secondary"
      @click="calendarDialog = true"
    />
  </div>

  <SportsMatchDialog
    v-if="dialog"
    v-model="dialog"
    :sport="editingSport"
    :match="editingMatch"
    :initial-date="initialDate"
  />
  <SportsMatchCalendar v-if="calendarDialog" v-model="calendarDialog" @create="createMatchOnDate" />
</template>

<style scoped>
.sports-match-editable {
  cursor: pointer;
}
</style>
