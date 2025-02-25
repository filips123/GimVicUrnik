import {
  addEventProcessor,
  browserTracingIntegration as originalBrowserTracingIntegration,
  captureException,
  getActiveSpan,
  getCurrentScope,
  getRootSpan,
  SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN,
  SEMANTIC_ATTRIBUTE_SENTRY_SOURCE,
  setHttpStatus,
  startBrowserTracingNavigationSpan,
} from '@sentry/browser'
import type { Integration, Span, SpanAttributes, TransactionSource } from '@sentry/core'
import {
  browserProfilingIntegration,
  browserSessionIntegration,
  extraErrorDataIntegration,
  httpClientIntegration,
  httpContextIntegration,
  init as sentryInit,
  reportingObserverIntegration,
  thirdPartyErrorFilterIntegration,
  vueIntegration,
} from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

import { useSettingsStore } from '@/stores/settings'

export default function registerSentry(app: App, router: Router) {
  if (!import.meta.env.VITE_SENTRY_ENABLED) return

  const { dataCollectionCrashes, dataCollectionPerformance } = useSettingsStore()
  if (!dataCollectionCrashes && !dataCollectionPerformance) return

  // Get release prefixes and suffixes from config
  const releasePrefix = import.meta.env.VITE_SENTRY_RELEASE_PREFIX || ''
  const releaseSuffix = import.meta.env.VITE_SENTRY_RELEASE_SUFFIX || ''

  // Get traces and profiles sample rates from config
  const tracesSampleRate = import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE
  const profilesSampleRate = import.meta.env.VITE_SENTRY_PROFILES_SAMPLE_RATE

  // Track only base components for performance
  const trackedComponents = [
    'VApp',
    'VAppBar',
    'VMain',
    'RouterView',
    'NavigationDesktop',
    'NavigationMobile',
    'NavigationDay',
    'ViewTimetable',
    'ViewMenu',
    'ViewCirculars',
    'ViewSources',
    'ViewNotifications',
    'ViewSettings',
    'ViewWelcome',
    'NotFound',
  ]

  // Include additional always-enabled integrations
  const integrations = [
    extraErrorDataIntegration({ depth: 8 }),
    reportingObserverIntegration(),
    httpClientIntegration(),
    httpContextIntegration(),
    thirdPartyErrorFilterIntegration({
      filterKeys: [import.meta.env.VITE_SENTRY_APPLICATION_KEY],
      behaviour: 'apply-tag-if-contains-third-party-frames',
    }),
    vueIntegration({
      tracingOptions: {
        trackComponents: dataCollectionPerformance ? trackedComponents : false,
      },
    }),
  ]

  // Add performance integrations if enabled in settings
  if (dataCollectionPerformance) {
    integrations.push(browserSessionIntegration())
    if (tracesSampleRate) integrations.push(browserTracingIntegration(router))
    if (profilesSampleRate) integrations.push(browserProfilingIntegration())
  }

  // Init the Sentry SDK
  sentryInit({
    app,

    dsn: import.meta.env.VITE_SENTRY_DSN,
    tracesSampleRate: tracesSampleRate,
    profilesSampleRate: profilesSampleRate,
    maxBreadcrumbs: import.meta.env.VITE_SENTRY_MAX_BREADCRUMBS,
    tracePropagationTargets: import.meta.env.VITE_SENTRY_TRACE_PROPAGATION_TARGETS,
    normalizeDepth: 8,

    environment: import.meta.env.MODE,
    release: releasePrefix + import.meta.env.VITE_VERSION + releaseSuffix,

    integrations,
  })

  // Add event processor to collect a few more useful metrics
  addEventProcessor(function (event) {
    // Make sure the context and tags objects exists
    if (!event.contexts) event.contexts = {}
    if (!event.tags) event.tags = {}

    // Add context from user settings that can be useful when debugging errors

    const settingsStore = useSettingsStore()

    event.contexts['Settings - General'] = {
      'Show Substitutions': settingsStore.showSubstitutions,
      'Show Links in Timetable': settingsStore.showLinksInTimetable,
      'Show Hours in Timetable': settingsStore.showHoursInTimetable,
      'Highlight Current Time': settingsStore.highlightCurrentTime,
      'Enable Lesson Details': settingsStore.enableLessonDetails,
      'Enable Pull To Refresh': settingsStore.enablePullToRefresh,
      'Theme Type': settingsStore.themeType,
      'Accent Color': settingsStore.accentColor,
    }

    event.contexts['Settings - Entity'] = {
      'Entity Type': settingsStore.entityType,
      'Entity List': settingsStore.entityList,
    }

    event.contexts['Settings - Food'] = {
      'Snack Type': settingsStore.snackType,
      'Lunch Type': settingsStore.lunchType,
    }

    // Add tags based on user settings

    event.tags['settings.show_substitutions'] = settingsStore.showSubstitutions
    event.tags['settings.show_links_in_timetable'] = settingsStore.showLinksInTimetable
    event.tags['settings.show_hours_in_timetable'] = settingsStore.showHoursInTimetable
    event.tags['settings.highlight_current_time'] = settingsStore.highlightCurrentTime
    event.tags['settings.enable_lesson_details'] = settingsStore.enableLessonDetails
    event.tags['settings.enable_pull_to_refresh'] = settingsStore.enablePullToRefresh
    event.tags['settings.accent_color'] = settingsStore.accentColor
    event.tags['settings.has_moodle_token'] = !!settingsStore.moodleToken
    event.tags['settings.has_circulars_password'] = !!settingsStore.circularsPassword
    event.tags['settings.type.theme'] = settingsStore.themeType
    event.tags['settings.type.entity'] = settingsStore.entityType
    event.tags['settings.type.snack'] = settingsStore.snackType
    event.tags['settings.type.lunch'] = settingsStore.lunchType

    // Add tags based on a few relevant media queries

    const displayModes = [
      'browser',
      'standalone',
      'fullscreen',
      'minimal-ui',
      'window-controls-overlay',
      'picture-in-picture',
    ]
    for (const displayMode of displayModes) {
      if (window.matchMedia(`(display-mode: ${displayMode})`).matches) {
        event.tags['media.display_mode'] = displayMode
        break
      }
    }

    const colorSchemes = ['light', 'dark']
    for (const colorScheme of colorSchemes) {
      if (window.matchMedia(`(prefers-color-scheme: ${colorScheme})`).matches) {
        event.tags['media.color_scheme'] = colorScheme
        break
      }
    }

    // Return the modified event
    return event
  })
}

/**
 * A custom browser tracing integration for Vue.
 *
 * Based on the original Sentry Vue instrumentation but modified to use our
 * custom transaction name formats and include more context data about events.
 *
 * Sources:
 * * https://github.com/getsentry/sentry-javascript/blob/develop/packages/vue/src/browserTracingIntegration.ts
 * * https://github.com/getsentry/sentry-javascript/blob/develop/packages/vue/src/router.ts
 */
function browserTracingIntegration(router: Router): Integration {
  const integration = originalBrowserTracingIntegration({ instrumentNavigation: false })

  const instrumentNavigation = true
  const instrumentPageLoad = true

  return {
    ...integration,

    afterAllSetup(client) {
      integration.afterAllSetup(client)

      router.onError(error => captureException(error, { mechanism: { handled: false } }))

      router.beforeEach((to, from) => {
        const attributes: SpanAttributes = {
          'route.name': to.name as string,
          'route.path': to.path as string,
          'route.hash': to.hash as string,
        }

        for (const key of Object.keys(to.params)) {
          attributes[`route.params.${key}`] = to.params[key]
        }

        for (const key of Object.keys(to.query)) {
          const value = to.query[key]
          if (value) attributes[`route.query.${key}`] = value
        }

        // Determine a name for the routing transaction
        let transactionName: string = to.path
        let transactionSource: TransactionSource = 'route'
        let transactionHttpStatus: number | undefined = undefined

        // Parametrize timetable transactions in the same style as backend
        if (
          to.name === 'timetable' &&
          ['classes', 'teachers', 'classrooms'].includes(to.params.type as string) &&
          to.params.value
        ) {
          if (!(to.params.type === 'classrooms' && to.params.value === 'empty')) {
            transactionName = to.matched[0].path
              .replace(':type?', to.params.type as string)
              .replace(':value?', `<${to.params.type}>`)
          }
        } else if (to.name === 'welcome') {
          transactionName = '/welcome'
          transactionSource = 'custom'
        } else if ((to.name === 'timetable' && to.params.type) || to.name === 'notFound') {
          transactionName = 'generic 404 request'
          transactionSource = 'custom'
          transactionHttpStatus = 404
        }

        getCurrentScope().setTransactionName(transactionName)

        const isPageLoadNavigation = from.name === undefined && from.matched.length === 0
        const isNotFoundNavigation = from.path === to.path && to.name === 'notFound'

        if (instrumentPageLoad && isPageLoadNavigation) {
          const activeRootSpan = getActiveRootSpan()
          if (activeRootSpan) {
            // Replace the name of the existing root span
            activeRootSpan.updateName(transactionName)

            // Set router attributes on the existing pageload transaction
            // This will override the source and origin and add params & query attributes
            activeRootSpan.setAttributes({
              ...attributes,
              [SEMANTIC_ATTRIBUTE_SENTRY_SOURCE]: transactionSource,
              [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: 'auto.pageload.vue',
            })

            // Set the HTTP status if it was specified
            if (transactionHttpStatus) {
              setHttpStatus(activeRootSpan, transactionHttpStatus)
            }
          }
        }

        if (instrumentNavigation && !isPageLoadNavigation && !isNotFoundNavigation) {
          attributes[SEMANTIC_ATTRIBUTE_SENTRY_SOURCE] = transactionSource
          attributes[SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN] = 'auto.navigation.vue'

          // Start a new navigation transaction
          const navigationSpan = startBrowserTracingNavigationSpan(client, {
            name: transactionName,
            op: 'navigation',
            attributes,
          })

          // Set the HTTP status if it was specified
          if (navigationSpan && transactionHttpStatus) {
            setHttpStatus(navigationSpan, transactionHttpStatus)
          }
        }
      })
    },
  }
}

function getActiveRootSpan(): Span | undefined {
  const span = getActiveSpan()
  if (span) return getRootSpan(span)
}
