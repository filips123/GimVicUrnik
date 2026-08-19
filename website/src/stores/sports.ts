import { defineStore } from 'pinia'

import { getCurrentDate, getISODate } from '@/utils/days'

export type SportSlug = 'football' | 'volleyball' | 'basketball'
export type SeasonPhase = 'setup' | 'group_stage' | 'knockout' | 'completed'
export type MatchStage = 'group' | 'quarterfinal' | 'semifinal' | 'third_place' | 'final'
export type MatchStatus = 'scheduled' | 'postponed' | 'completed' | 'forfeited'
export type GroupName = 'A' | 'B' | 'C' | 'D'

export const sports: SportSlug[] = ['football', 'volleyball', 'basketball']
export const sportNames: Record<SportSlug, string> = {
  football: 'Nogomet',
  volleyball: 'Odbojka',
  basketball: 'Košarka',
}

export interface SportsRule {
  id: number | null
  position: number
  text: string
  url: string | null
}

export interface VolleyballSet {
  number?: number
  homeScore: number | null
  awayScore: number | null
}

export interface SportsMatch {
  id: number
  stage: MatchStage
  status: MatchStatus
  group: GroupName | null
  bracketSlot: string | null
  date: string | null
  time: string
  homeClass: string | null
  homeName: string | null
  awayClass: string | null
  awayName: string | null
  homeScore: number | null
  awayScore: number | null
  homePenalties: number | null
  awayPenalties: number | null
  forfeitWinner: string | null
  notes: string | null
  sets: VolleyballSet[]
  revision: number
}

export interface StandingRow {
  rank: number
  classCode: string
  className: string
  played: number
  won: number
  drawn?: number
  lost: number
  scored?: number
  conceded?: number
  difference?: number
  setsWon?: number
  setsLost?: number
  points: number
  qualifiedRank: number | null
}

export interface SportsGroupData {
  name: GroupName
  participants: { classCode: string; className: string; qualifiedRank: number | null }[]
  standings: StandingRow[]
  matches: SportsMatch[]
}

export interface QualificationTie {
  group: GroupName
  classCodes: string[]
  classNames: string[]
  resolved: boolean
}

export interface SportsSeason {
  exists: boolean
  sport: SportSlug
  sportName: string
  seasonKey: string
  seasonLabel: string
  phase: SeasonPhase
  revision: number
  availableClasses: string[]
  rules: SportsRule[]
  groups: SportsGroupData[]
  qualificationTies: QualificationTie[]
  qualificationDecisions: { group: GroupName; orderedClasses: string[]; reason: string }[]
  bracket: SportsMatch[]
  podium: { gold: string; silver: string; bronze: string } | null
}

export interface ScheduleMatch extends SportsMatch {
  sport: SportSlug
  sportName: string
  seasonKey: string
}

export interface AdminSession {
  authenticated: boolean
  sport: SportSlug | null
  csrfToken: string
  expires: string | null
}

export class SportsApiError extends Error {
  status: number
  details: Record<string, any>

  constructor(status: number, message: string, details: Record<string, any> = {}) {
    super(message)
    this.status = status
    this.details = details
  }
}

const conditionalCache = new Map<string, { etag: string; value: unknown }>()

async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const isPublicRead = !options.method || options.method === 'GET'
  const cached = isPublicRead ? conditionalCache.get(path) : undefined
  const response = await fetch(import.meta.env.VITE_API + path, {
    credentials: 'include',
    ...(isPublicRead ? { cache: 'no-cache' as RequestCache } : {}),
    ...options,
    headers: {
      ...(cached?.etag ? { 'If-None-Match': cached.etag } : {}),
      ...(options.headers || {}),
    },
  })

  if (response.status === 304 && cached) return cached.value as T

  const value = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new SportsApiError(
      response.status,
      value?.error?.description || value?.message || 'Prišlo je do napake.',
      value,
    )
  }

  const etag = response.headers?.get?.('ETag')
  if (isPublicRead && etag) conditionalCache.set(path, { etag, value })
  return value
}

function localSchoolYear(): string {
  const date = getCurrentDate()
  const start = date.getMonth() >= 8 ? date.getFullYear() : date.getFullYear() - 1
  return `${start}-${String(start + 1).slice(-2)}`
}

export const useSportsStore = defineStore('sports', {
  state: () => ({
    currentSeasonKey: localSchoolYear(),
    selectedSeasonKey: localSchoolYear(),
    availableSeasons: [] as {
      sport: SportSlug
      seasonKey: string
      seasonLabel: string
      phase: SeasonPhase
    }[],
    seasons: {} as Partial<Record<SportSlug, SportsSeason>>,
    scheduleWeekStart: '',
    scheduleDays: [[], [], [], [], []] as ScheduleMatch[][],
    admin: {
      authenticated: false,
      sport: null,
      csrfToken: '',
      expires: null,
    } as AdminSession,
  }),

  getters: {
    activeSeason: state => (sport: SportSlug) => state.seasons[sport],
    canEdit: state => (sport: SportSlug) =>
      state.admin.authenticated && state.admin.sport === sport,
  },

  actions: {
    async updateSeasonList() {
      const value = await api<{
        currentSeasonKey: string
        seasons: { sport: SportSlug; seasonKey: string; seasonLabel: string; phase: SeasonPhase }[]
      }>('/sports/seasons')
      this.currentSeasonKey = value.currentSeasonKey
      this.selectedSeasonKey = value.currentSeasonKey
      this.availableSeasons = value.seasons
    },

    async updateSport(sport: SportSlug, seasonKey?: string) {
      const targetSeason = seasonKey || this.selectedSeasonKey
      this.seasons[sport] = await api<SportsSeason>(`/sports/${sport}/seasons/${targetSeason}`)
    },

    async updateSchedule(date: string) {
      const value = await api<{ weekStart: string; days: ScheduleMatch[][] }>(
        `/sports/schedule/week/${date}`,
      )
      this.scheduleWeekStart = value.weekStart
      this.scheduleDays = value.days
    },

    async getScheduleWeeks(dates: string[]) {
      const weeks = await Promise.all(
        dates.map(date =>
          api<{ weekStart: string; days: ScheduleMatch[][] }>(`/sports/schedule/week/${date}`),
        ),
      )
      return weeks.flatMap(week => week.days.flat())
    },

    async restoreAdminSession() {
      const value = await api<
        | { authenticated: false }
        | { authenticated: true; sport: SportSlug; csrfToken: string; expires: string }
      >('/sports/admin/session')
      this.admin = value.authenticated
        ? {
            authenticated: true,
            sport: value.sport,
            csrfToken: value.csrfToken,
            expires: value.expires,
          }
        : { authenticated: false, sport: null, csrfToken: '', expires: null }
    },

    async login(sport: SportSlug, password: string) {
      const value = await api<{
        authenticated: true
        sport: SportSlug
        csrfToken: string
        expires: string
        currentSeasonKey: string
      }>('/sports/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sport, password }),
      })
      this.admin = {
        authenticated: true,
        sport: value.sport,
        csrfToken: value.csrfToken,
        expires: value.expires,
      }
      this.currentSeasonKey = value.currentSeasonKey
    },

    async logout() {
      await this.adminRequest('/sports/admin/logout', { method: 'POST', body: '{}' })
      this.admin = { authenticated: false, sport: null, csrfToken: '', expires: null }
    },

    async adminRequest<T>(path: string, options: RequestInit): Promise<T> {
      return api<T>(path, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.admin.csrfToken,
          ...(options.headers || {}),
        },
      })
    },

    async saveGroups(sport: SportSlug, groups: Record<GroupName, string[]>) {
      const season = this.seasons[sport]!
      this.seasons[sport] = await this.adminRequest<SportsSeason>(
        `/sports/${sport}/seasons/${season.seasonKey}/setup`,
        { method: 'PUT', body: JSON.stringify({ revision: season.revision, groups }) },
      )
    },

    async saveRules(sport: SportSlug, rules: { text: string; url: string | null }[]) {
      const season = this.seasons[sport]!
      this.seasons[sport] = await this.adminRequest<SportsSeason>(
        `/sports/${sport}/seasons/${season.seasonKey}/rules`,
        { method: 'PATCH', body: JSON.stringify({ revision: season.revision, rules }) },
      )
    },

    async createMatch(
      sport: SportSlug,
      data: Record<string, any>,
    ): Promise<{ warnings?: string[] }> {
      const season = this.seasons[sport]!
      try {
        const value = await this.adminRequest<{ season: SportsSeason }>(
          `/sports/${sport}/seasons/${season.seasonKey}/matches`,
          { method: 'POST', body: JSON.stringify({ revision: season.revision, ...data }) },
        )
        this.seasons[sport] = value.season
        await this.updateSchedule(data.date)
        return {}
      } catch (error) {
        if (error instanceof SportsApiError && error.details.requiresConfirmation) {
          return { warnings: error.details.warnings }
        }
        throw error
      }
    },

    async updateMatch(
      sport: SportSlug,
      match: SportsMatch,
      data: Record<string, any>,
    ): Promise<{ warnings?: string[] }> {
      const season = this.seasons[sport]!
      try {
        const value = await this.adminRequest<{ season: SportsSeason }>(
          `/sports/${sport}/seasons/${season.seasonKey}/matches/${match.id}`,
          {
            method: 'PATCH',
            body: JSON.stringify({
              revision: season.revision,
              matchRevision: match.revision,
              ...data,
            }),
          },
        )
        this.seasons[sport] = value.season
        await this.updateSchedule(data.date || match.date || getISODate(getCurrentDate()))
        return {}
      } catch (error) {
        if (error instanceof SportsApiError && error.details.requiresConfirmation) {
          return { warnings: error.details.warnings }
        }
        throw error
      }
    },

    async deleteMatch(sport: SportSlug, match: SportsMatch) {
      const season = this.seasons[sport]!
      this.seasons[sport] = await this.adminRequest<SportsSeason>(
        `/sports/${sport}/seasons/${season.seasonKey}/matches/${match.id}`,
        {
          method: 'DELETE',
          body: JSON.stringify({ revision: season.revision, matchRevision: match.revision }),
        },
      )
      await this.updateSchedule(match.date || getISODate(getCurrentDate()))
    },

    async closeGroupStage(
      sport: SportSlug,
      tieDecisions: { group: GroupName; orderedClasses: string[]; reason: string }[],
    ) {
      await this.seasonAction(sport, 'group-stage/close', { tieDecisions })
    },

    async reopenGroupStage(sport: SportSlug) {
      await this.seasonAction(sport, 'group-stage/reopen', { confirm: true })
    },

    async assignQuarterfinals(sport: SportSlug, slots: Record<string, string[]>) {
      const season = this.seasons[sport]!
      this.seasons[sport] = await this.adminRequest<SportsSeason>(
        `/sports/${sport}/seasons/${season.seasonKey}/bracket/quarterfinals`,
        { method: 'PUT', body: JSON.stringify({ revision: season.revision, slots }) },
      )
    },

    async completeSeason(sport: SportSlug) {
      await this.seasonAction(sport, 'complete')
    },

    async reopenSeason(sport: SportSlug) {
      await this.seasonAction(sport, 'reopen')
    },

    async seasonAction(sport: SportSlug, action: string, extra: Record<string, any> = {}) {
      const season = this.seasons[sport]!
      this.seasons[sport] = await this.adminRequest<SportsSeason>(
        `/sports/${sport}/seasons/${season.seasonKey}/${action}`,
        { method: 'POST', body: JSON.stringify({ revision: season.revision, ...extra }) },
      )
    },
  },

  persist: {
    pick: [
      'currentSeasonKey',
      'selectedSeasonKey',
      'availableSeasons',
      'seasons',
      'scheduleWeekStart',
      'scheduleDays',
    ],
  },
})
