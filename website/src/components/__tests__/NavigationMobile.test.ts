import { shallowMount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import NavigationMobile from '@/components/NavigationMobile.vue'

describe('sports administrator long press', () => {
  afterEach(() => vi.useRealTimers())

  it('opens administrator login after holding the sports button', async () => {
    vi.useFakeTimers()
    const wrapper = shallowMount(NavigationMobile, {
      props: {
        navigation: [{ title: 'Tekme', link: 'sports', icon: 'icon' }],
      },
      global: {
        stubs: {
          'v-bottom-navigation': { template: '<div><slot /></div>' },
          'v-btn': { template: '<button />' },
        },
      },
    })

    await wrapper.find('button').trigger('pointerdown')
    vi.advanceTimersByTime(700)

    expect(wrapper.emitted('sportsAdmin')).toHaveLength(1)
  })

  it('does not open administrator login after a normal tap', async () => {
    vi.useFakeTimers()
    const wrapper = shallowMount(NavigationMobile, {
      props: {
        navigation: [{ title: 'Tekme', link: 'sports', icon: 'icon' }],
      },
      global: {
        stubs: {
          'v-bottom-navigation': { template: '<div><slot /></div>' },
          'v-btn': { template: '<button />' },
        },
      },
    })
    const button = wrapper.find('button')

    await button.trigger('pointerdown')
    vi.advanceTimersByTime(200)
    await button.trigger('pointerup')
    vi.advanceTimersByTime(700)

    expect(wrapper.emitted('sportsAdmin')).toBeUndefined()
  })
})
