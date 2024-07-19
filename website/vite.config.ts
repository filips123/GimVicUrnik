import * as process from 'node:process'
import { fileURLToPath, URL } from 'node:url'

import { sentryVitePlugin as SentryVite } from '@sentry/vite-plugin'
import Vue, { Options as VueOptions } from '@vitejs/plugin-vue'
import { defineConfig, loadEnv, PluginOption } from 'vite'
import { createHtmlPlugin as Html } from 'vite-plugin-html'
import { VitePWA, VitePWAOptions } from 'vite-plugin-pwa'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

import { version as appVersion } from './package.json'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  if (!env.VITE_TITLE) {
    // Show a helpful message when the required environment variables are not set
    console.error('Environment variables are not set, make sure you have copied the config file')
    process.exit(1)
  }

  // Use Vuetify's template to resolve asset URLs passed to Vuetify components
  const vueConfig: VueOptions = {
    template: { transformAssetUrls },
  }

  // Use HTML plugin to minify built HTML and autoinject scripts
  const htmlConfig = {
    entry: 'src/main.ts',
    template: 'index.html',
    minify: true,
  }

  const pwaConfig: Partial<VitePWAOptions & { manifest: { keywords: string[] } }> = {
    manifestFilename: 'site.webmanifest',

    // TODO: Configure service worker registration and updates

    manifest: {
      name: env.VITE_TITLE,
      short_name: env.VITE_SHORT,
      description: env.VITE_DESCRIPTION,
      categories: env.VITE_CATEGORIES.split(','),
      keywords: env.VITE_KEYWORDS.split(','),
      lang: 'sl',

      theme_color: '#007300',
      background_color: '#ffffff',

      icons: [
        { src: '/img/icons/favicon.svg', type: 'image/svg+xml', sizes: 'any' },
        { src: '/img/icons/favicon-maskable.svg', type: 'image/svg+xml', sizes: 'any', purpose: 'maskable' },
        { src: '/img/icons/favicon-monochrome.svg', type: 'image/svg+xml', sizes: 'any', purpose: 'monochrome' },
        // We still need to include PNG icons because Safari does not support SVG icons
        // The old `android-chrome` name is kept for compatibility with existing installations
        { src: '/img/icons/android-chrome-192x192.png', type: 'image/png', sizes: '192x192' },
        { src: '/img/icons/android-chrome-512x512.png', type: 'image/png', sizes: '512x512' },
        { src: '/img/icons/android-chrome-maskable-192x192.png', type: 'image/png', sizes: '192x192', purpose: 'maskable' },
        { src: '/img/icons/android-chrome-maskable-512x512.png', type: 'image/png', sizes: '512x512', purpose: 'maskable' },
      ],

      shortcuts: [
        {
          name: 'Urnik',
          url: '/timetable',
          icons: [{ src: '/img/shortcuts/timetable.png', type: 'image/png', sizes: '192x192' }],
        },
        {
          name: 'Jedilnik',
          url: '/menu',
          icons: [{ src: '/img/shortcuts/menu.png', type: 'image/png', sizes: '192x192' }],
        },
        {
          name: 'Okrožnice',
          url: '/circulars',
          icons: [{ src: '/img/shortcuts/circulars.png', type: 'image/png', sizes: '192x192' }],
        },
      ],
    },

    devOptions: {
      enabled: true,
      suppressWarnings: true
    }
  }

  const plugins: PluginOption = [
    Vue(vueConfig),
    Vuetify(),
    Html(htmlConfig),
    VitePWA(pwaConfig),
  ]

  // Upload sourcemaps for the current release to Sentry if enabled
  if (env.SENTRY_UPLOAD_SOURCEMAPS === 'true') {
    const releasePrefix = env.VITE_SENTRY_RELEASE_PREFIX || ''
    const releaseSuffix = env.VITE_SENTRY_RELEASE_SUFFIX || ''
    const releaseVersion = releasePrefix + appVersion + releaseSuffix

    plugins.push(SentryVite({
      org: env.SENTRY_ORG,
      project: env.SENTRY_PROJECT,
      authToken: env.SENTRY_AUTH_TOKEN,
      applicationKey: env.VITE_SENTRY_APPLICATION_KEY,
      release: { name: releaseVersion, create: false, finalize: false },
    }))
  }

  return {
    plugins,

    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '$': fileURLToPath(new URL('./public', import.meta.url)),
      },
    },

    define: {
      'import.meta.env.VITE_VERSION': JSON.stringify(appVersion),
      'import.meta.env.VITE_BUILDTIME': new Date(),
    },

    build: {
      sourcemap: true,
      rollupOptions: {
        output: {
          // Use Webpack prefix for easier matching
          sourcemapPathTransform: file => {
            file = file.replace(/^(\.\.\/|\.\.\\)*/, '')
            return `webpack://${file}`
          },

          // Use HEX hashing because it looks nicer
          hashCharacters: 'hex',

          // Split assets into directory per type for easier server config
          entryFileNames: 'js/[name].[hash].js',
          chunkFileNames: 'js/[name].[hash].js',
          assetFileNames: ({ name }) => {
            const extension = name!.split('.').at(1)
            if (extension === 'css') return 'css/[name].[hash][extname]'
            if (/svg|png|jpe?g|gif|ico|bmp|tiff|webp/.test(extension!)) return 'img/[name].[hash][extname]'
            if (/woff|woff2|eot|ttf|otf/.test(extension!)) return 'font/[name].[hash][extname]'
            return 'assets/[name].[hash][extname]'
          },
        },
      },
    },
  }
})
