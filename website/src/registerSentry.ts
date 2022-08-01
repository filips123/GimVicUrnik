/* eslint-disable simple-import-sort/imports */

import Vue from 'vue'
import VueRouter from 'vue-router'

import { init as sentryInit } from '@sentry/vue'
import { VueRouterInstrumentation } from '@sentry/vue/types/router'
import { captureException } from '@sentry/browser'
import { Transaction, TransactionContext, TransactionSource } from '@sentry/types'
import { Integrations } from '@sentry/tracing'

import router from '@/router'
import { SettingsModule } from '@/store/modules/settings'

// Only load Sentry if it is enabled by build config and user settings
if (process.env.VUE_APP_SENTRY_ENABLED === 'true' && (SettingsModule.dataCollection.performance || SettingsModule.dataCollection.crashes)) {
  // Custom Vue Router instrumentation for Sentry
  function vueRouterInstrumentation (router: VueRouter): VueRouterInstrumentation {
    return (
      startTransaction: (context: TransactionContext) => Transaction | undefined,
      startTransactionOnPageLoad = true,
      startTransactionOnLocationChange = true
    ) => {
      router.onError(error => captureException(error))

      const tags = { 'routing.instrumentation': 'vue-router' }

      router.beforeEach((to, from, next) => {
        const data = {
          name: to.name,
          path: to.path,
          params: to.params,
          query: to.query,
          hash: to.hash
        }

        // Determine transaction name based on route's path
        let transactionName = to.path
        let transactionSource: TransactionSource = 'url'

        // Parametrize timetable transactions in the same style as backend
        if (to.name === 'timetable' && ['classes', 'teachers', 'classrooms'].includes(to.params.type) && to.params.value) {
          if (!(to.params.type === 'classrooms' && to.params.value === 'empty')) {
            transactionName = to.matched[0].path.replace(':type?', to.params.type).replace(':value?', `<${to.params.type}>`)
            transactionSource = 'route'
          }

        // Create 404 transaction when a valid entity hasn't been found
        } else if ((to.name === 'timetable' && to.params.type) || to.name === 'notfound') {
          transactionName = 'generic 404 request'
          transactionSource = 'custom'
        }

        const isPageLoadNavigation = from.name == null && from.matched.length === 0
        const isNotFoundNavigation = from.path === to.path && to.name === 'notfound'

        if (startTransactionOnPageLoad && isPageLoadNavigation) {
          startTransaction({
            name: transactionName,
            op: 'pageload',
            tags,
            data,
            metadata: {
              source: transactionSource
            }
          })
        }

        if (startTransactionOnLocationChange && !isPageLoadNavigation && !isNotFoundNavigation) {
          startTransaction({
            name: transactionName,
            op: 'navigation',
            tags,
            data,
            metadata: {
              source: transactionSource
            }
          })
        }

        next()
      })
    }
  }

  // Release prefixes and suffixes from config
  const releasePrefix = process.env.VUE_APP_SENTRY_RELEASE_PREFIX || ''
  const releaseSuffix = process.env.VUE_APP_SENTRY_RELEASE_SUFFIX || ''

  // Don't add performance monitoring to users who don't want it
  const integrations = []
  if (SettingsModule.dataCollection.performance) {
    integrations.push(
      new Integrations.BrowserTracing({
        tracingOrigins: process.env.VUE_APP_SENTRY_TRACING_ORIGINS.split(','),
        routingInstrumentation: vueRouterInstrumentation(router)
      })
    )
  }

  // Init the Sentry SDK
  sentryInit({
    Vue,

    dsn: process.env.VUE_APP_SENTRY_DSN,
    tracesSampleRate: parseFloat(process.env.VUE_APP_SENTRY_SAMPLE_RATE),
    maxBreadcrumbs: parseInt(process.env.VUE_APP_SENTRY_MAX_BREADCRUMBS),

    environment: process.env.NODE_ENV,
    release: releasePrefix + process.env.VUE_APP_VERSION + releaseSuffix,

    logErrors: !(process.env.NODE_ENV === 'production'),
    autoSessionTracking: SettingsModule.dataCollection.performance,
    tracingOptions: { trackComponents: true },

    integrations
  })
}
