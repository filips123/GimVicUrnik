import {
  browserProfilingIntegration,
  browserTracingIntegration,
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

  // TODO: Custom router instrumentation

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
    integrations.push(browserTracingIntegration({ router }))
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
