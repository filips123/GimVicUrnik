/* eslint-disable simple-import-sort/imports */

import Vue from 'vue'
import VueRouter from 'vue-router'

import { init } from '@sentry/vue'
import { VueRouterInstrumentation } from '@sentry/vue/dist/vuerouter'
import { captureException } from '@sentry/browser'
import { Transaction, TransactionContext } from '@sentry/types'
import { Integrations } from '@sentry/tracing'

import router from '@/router'
import { SettingsModule } from '@/store/modules/settings'

if (process.env.VUE_APP_SENTRY_ENABLED === 'true') {
  let firstLoad = true

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

        let opName = to.path

        if (to.name === 'timetable' && ['classes', 'teachers', 'classrooms'].includes(to.params.type) && to.params.value) {
          if (!(to.params.type === 'classrooms' && to.params.value === 'empty')) {
            opName = to.matched[0].path.replace(':type?', to.params.type).replace(':value?', `<${to.params.type}>`)
          }
        } else if ((to.name === 'timetable' && to.params.type) || to.name === 'notfound') {
          opName = 'generic 404 request'
        }

        const isNotFoundRedirection = from.path === to.path && to.name === 'notfound'

        if (startTransactionOnPageLoad && firstLoad) {
          startTransaction({
            name: opName,
            op: 'pageload',
            tags,
            data
          })
        }

        if (startTransactionOnLocationChange && !firstLoad && !isNotFoundRedirection) {
          startTransaction({
            name: opName,
            op: 'navigation',
            tags,
            data
          })
        }

        firstLoad = false
        next()
      })
    }
  }

  // Release prefixes and suffixes from config
  const releasePrefix = process.env.VUE_APP_SENTRY_RELEASE_PREFIX ? process.env.VUE_APP_SENTRY_RELEASE_PREFIX : ''
  const releaseSuffix = process.env.VUE_APP_SENTRY_RELEASE_SUFFIX ? process.env.VUE_APP_SENTRY_RELEASE_SUFFIX : ''

  // Don't add performance monitoring to users who don't want it
  const integrations = []
  if (!SettingsModule.doNotTrack) {
    integrations.push(
      new Integrations.BrowserTracing({
        tracingOrigins: process.env.VUE_APP_SENTRY_TRACING_ORIGINS.split(','),
        routingInstrumentation: vueRouterInstrumentation(router)
      })
    )
  }

  // Init the Sentry SDK
  init({
    Vue,

    dsn: process.env.VUE_APP_SENTRY_DSN,
    tracesSampleRate: parseFloat(process.env.VUE_APP_SENTRY_SAMPLE_RATE),
    maxBreadcrumbs: parseInt(process.env.VUE_APP_SENTRY_MAX_BREADCRUMBS),

    environment: process.env.NODE_ENV,
    release: releasePrefix + process.env.VUE_APP_VERSION + releaseSuffix,

    logErrors: !(process.env.NODE_ENV === 'production'),
    autoSessionTracking: true,
    tracingOptions: { trackComponents: true },

    integrations: integrations
  })
}
