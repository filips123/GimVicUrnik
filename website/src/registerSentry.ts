import { Integrations } from '@sentry/tracing'
import { init } from '@sentry/vue'
import Vue from 'vue'

if (process.env.VUE_APP_SENTRY_ENABLED === 'true') {
  init({
    Vue: Vue,

    dsn: process.env.VUE_APP_SENTRY_DSN,
    sampleRate: parseFloat(process.env.VUE_APP_SENTRY_TRACES),
    maxBreadcrumbs: parseInt(process.env.VUE_APP_SENTRY_BREADCRUMBS),

    environment: process.env.NODE_ENV,
    release: process.env.VUE_APP_VERSION,

    logErrors: !(process.env.NODE_ENV === 'production'),
    autoSessionTracking: true,
    tracingOptions: {
      trackComponents: true
    },
    integrations: [
      new Integrations.BrowserTracing()
    ]
  })
}
