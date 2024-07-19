/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />
/// <reference types="vite-plugin-pwa/info" />

interface ImportMetaEnv {
  readonly VITE_TITLE: string
  readonly VITE_SHORT: string
  readonly VITE_DESCRIPTION: string
  readonly VITE_CATEGORIES: string
  readonly VITE_KEYWORDS: string

  readonly VITE_WEBSITE: string
  readonly VITE_API: string

  readonly VITE_ECLASSROOM_WEBSERVICE: string
  readonly VITE_ECLASSROOM_NORMAL: string

  readonly VITE_CIRCULARS_PASSWORD: string

  readonly VITE_SENTRY_DSN: string
  readonly VITE_SENTRY_ENABLED: string
  readonly VITE_SENTRY_MAX_BREADCRUMBS: string
  readonly VITE_SENTRY_TRACES_SAMPLE_RATE: string
  readonly VITE_SENTRY_PROFILES_SAMPLE_RATE: string
  readonly VITE_SENTRY_TRACE_PROPAGATION_TARGETS: string
  readonly VITE_SENTRY_APPLICATION_KEY: string
  readonly VITE_SENTRY_RELEASE_PREFIX: string
  readonly VITE_SENTRY_RELEASE_SUFFIX: string

  readonly VITE_VERSION: string
  readonly VITE_BUILDTIME: string

  readonly VITE_CUSTOM_DATE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface Navigator {
  globalPrivacyControl: boolean | undefined
}
