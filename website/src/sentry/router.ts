// Modified Vue Router instrumentation, so we can preserve our custom transaction name formats
// Source: https://github.com/getsentry/sentry-javascript/blob/develop/packages/vue/src/router.ts

import { captureException } from '@sentry/browser'
import {
  getActiveSpan,
  getRootSpan,
  SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN,
  SEMANTIC_ATTRIBUTE_SENTRY_SOURCE,
  spanToJSON,
} from '@sentry/core'
import type { Span, SpanAttributes, TransactionContext, TransactionSource } from '@sentry/types'
import type { Router } from 'vue-router'

export function instrumentVueRouter(
  router: Router,
  options: {
    routeLabel: 'name' | 'path'
    instrumentPageLoad: boolean
    instrumentNavigation: boolean
  },
  startNavigationSpanFn: (context: TransactionContext) => void,
): void {
  router.onError(error => captureException(error, { mechanism: { handled: false } }))

  router.beforeEach((to, from) => {
    const isPageLoadNavigation = from.name == null && from.matched.length === 0

    const attributes: SpanAttributes = {
      [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: 'auto.navigation.vue',
    }

    for (const key of Object.keys(to.params)) {
      attributes[`params.${key}`] = to.params[key]
    }

    for (const key of Object.keys(to.query)) {
      const value = to.query[key]
      if (value) attributes[`query.${key}`] = value
    }

    // Determine a name for the routing transaction and where that name came from
    let transactionName: string = to.path
    let transactionSource: TransactionSource = 'url'
    if (to.name && options.routeLabel !== 'path') {
      transactionName = to.name.toString()
      transactionSource = 'custom'
    } else if (to.matched[0] && to.matched[0].path) {
      transactionName = to.matched[0].path
      transactionSource = 'route'
    }

    if (options.instrumentPageLoad && isPageLoadNavigation) {
      const activeRootSpan = getActiveRootSpan()
      if (activeRootSpan) {
        const existingAttributes = spanToJSON(activeRootSpan).data || {}
        if (existingAttributes[SEMANTIC_ATTRIBUTE_SENTRY_SOURCE] !== 'custom') {
          activeRootSpan.updateName(transactionName)
          activeRootSpan.setAttribute(SEMANTIC_ATTRIBUTE_SENTRY_SOURCE, transactionSource)
        }
        // Set router attributes on the existing pageload transaction
        // This will override the origin, and add params & query attributes
        activeRootSpan.setAttributes({
          ...attributes,
          [SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN]: 'auto.pageload.vue',
        })
      }
    }

    if (options.instrumentNavigation && !isPageLoadNavigation) {
      attributes[SEMANTIC_ATTRIBUTE_SENTRY_SOURCE] = transactionSource
      attributes[SEMANTIC_ATTRIBUTE_SENTRY_ORIGIN] = 'auto.navigation.vue'
      startNavigationSpanFn({
        name: transactionName,
        op: 'navigation',
        attributes,
      })
    }
  })
}

function getActiveRootSpan(): Span | undefined {
  const span = getActiveSpan()
  const rootSpan = span ? getRootSpan(span) : undefined

  if (!rootSpan) {
    return undefined
  }

  const op = spanToJSON(rootSpan).op

  // Only use this root span if it is a pageload or navigation span
  return op === 'navigation' || op === 'pageload' ? rootSpan : undefined
}
