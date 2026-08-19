import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { sportNames, useSportsStore } from '@/stores/sports'

describe('sports store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('uses Slovenian sport names', () => {
    expect(sportNames).toEqual({
      football: 'Nogomet',
      volleyball: 'Odbojka',
      basketball: 'Košarka',
    })
  })

  it('loads a public empty season', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          exists: false,
          sport: 'football',
          sportName: 'Nogomet',
          seasonKey: '2025-26',
          seasonLabel: '2025/26',
          phase: 'setup',
          revision: 0,
          availableClasses: [],
          rules: [],
          groups: [],
          qualificationTies: [],
          qualificationDecisions: [],
          bracket: [],
          podium: null,
        }),
      }),
    )

    const store = useSportsStore()
    await store.updateSport('football', '2025-26')

    expect(store.seasons.football?.exists).toBe(false)
    expect(store.seasons.football?.seasonLabel).toBe('2025/26')
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/sports/football/seasons/2025-26'),
      expect.objectContaining({ credentials: 'include' }),
    )
  })
})
