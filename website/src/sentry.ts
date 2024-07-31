import {
  browserTracingIntegration as originalBrowserTracingIntegration,
  captureException,
  getActiveSpan,
  getCurrentScope,
  getRootSpan,
  SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN,
  SEMANTIC_ATTRIBUTE_SENTRY_SOURCE,
  spanToJSON,
  startBrowserTracingNavigationSpan,
} from '@sentry/browser'
import type { Integration, Span, SpanAttributes, TransactionSource } from '@sentry/types'
import {
  browserProfilingIntegration,
  extraErrorDataIntegration,
  httpClientIntegration,
  init as sentryInit,
  reportingObserverIntegration,
  thirdPartyErrorFilterIntegration,
} from '@sentry/vue'
import type { App } from 'vue'
import type { Router } from 'vue-router'

import { useSettingsStore } from '@/stores/settings'

export default function registerSentry(app: App, router: Router) {
  if (import.meta.env.VITE_SENTRY_ENABLED !== 'true') return

  const { dataCollectionCrashes, dataCollectionPerformance } = useSettingsStore()
  if (!dataCollectionCrashes && !dataCollectionPerformance) return

  // Release prefixes and suffixes from config
  const releasePrefix = import.meta.env.VITE_SENTRY_RELEASE_PREFIX || ''
  const releaseSuffix = import.meta.env.VITE_SENTRY_RELEASE_SUFFIX || ''

  // Include additional always-enabled integrations
  const integrations = [
    extraErrorDataIntegration({ depth: 8 }),
    reportingObserverIntegration(),
    httpClientIntegration(),
    thirdPartyErrorFilterIntegration({
      filterKeys: [import.meta.env.VITE_SENTRY_APPLICATION_KEY],
      behaviour: 'apply-tag-if-contains-third-party-frames',
    }),
  ]

  // Add performance integrations if enabled in settings
  if (dataCollectionPerformance) {
    integrations.push(browserTracingIntegration(router))
    integrations.push(browserProfilingIntegration())
  }

  // Init the Sentry SDK
  sentryInit({
    app,

    dsn: import.meta.env.VITE_SENTRY_DSN,
    tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE),
    profilesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_PROFILES_SAMPLE_RATE),
    maxBreadcrumbs: parseInt(import.meta.env.VITE_SENTRY_MAX_BREADCRUMBS),
    tracePropagationTargets: import.meta.env.VITE_SENTRY_TRACE_PROPAGATION_TARGETS.split(','),
    normalizeDepth: 8,

    environment: import.meta.env.MODE,
    release: releasePrefix + import.meta.env.VITE_VERSION + releaseSuffix,

    autoSessionTracking: dataCollectionPerformance,
    trackComponents: dataCollectionPerformance,

    integrations,
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
          [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: 'auto.navigation.vue',
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
        } else if ((to.name === 'timetable' && to.params.type) || to.name === 'notFound') {
          transactionName = 'generic 404 request'
          transactionSource = 'custom'
        }

        getCurrentScope().setTransactionName(transactionName)

        const isPageLoadNavigation = from.name === undefined && from.matched.length === 0
        const isNotFoundNavigation = from.path === to.path && to.name === 'notFound'

        if (instrumentPageLoad && isPageLoadNavigation) {
          const activeRootSpan = getActiveRootSpan()
          if (activeRootSpan) {
            // Replace the name of the existing root span if it was not custom set
            const existingAttributes = spanToJSON(activeRootSpan).data || {}
            if (existingAttributes[SEMANTIC_ATTRIBUTE_SENTRY_SOURCE] !== 'custom') {
              activeRootSpan.updateName(transactionName)
              activeRootSpan.setAttribute(SEMANTIC_ATTRIBUTE_SENTRY_SOURCE, transactionSource)
            }

            // Set router attributes on the existing pageload transaction
            // This will override the origin and add params & query attributes
            activeRootSpan.setAttributes({
              ...attributes,
              [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: 'auto.pageload.vue',
            })
          }
        }

        if (instrumentNavigation && !isPageLoadNavigation && !isNotFoundNavigation) {
          attributes[SEMANTIC_ATTRIBUTE_SENTRY_SOURCE] = transactionSource
          attributes[SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN] = 'auto.navigation.vue'

          // Start a new navigation transaction
          startBrowserTracingNavigationSpan(client, {
            name: transactionName,
            op: 'navigation',
            attributes,
          })
        }
      })
    },
  }
}

function getActiveRootSpan(): Span | undefined {
  const span = getActiveSpan()
  const rootSpan = span && getRootSpan(span)

  if (!rootSpan) {
    return undefined
  }

  const op = spanToJSON(rootSpan).op

  // Only use this root span if it is a pageload or navigation span
  return op === 'navigation' || op === 'pageload' ? rootSpan : undefined
}
