import { fileURLToPath, URL } from 'node:url'

import Vue, { Options as VueOptions } from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'
import { createHtmlPlugin as Html } from 'vite-plugin-html'
import { VitePWA, VitePWAOptions } from 'vite-plugin-pwa'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  if (!env.VITE_TITLE) {
    // Show a helpful message when the required environment variables are not set
    throw Error('Environment variables are not set, make sure you have copied the config file')
  }

  const vueConfig: VueOptions = {
    template: { transformAssetUrls },
  }

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
          url: '/menus',
          icons: [{ src: '/img/shortcuts/menus.png', type: 'image/png', sizes: '192x192' }],
        },
        {
          name: 'Okrožnice',
          url: '/circulars',
          icons: [{ src: '/img/shortcuts/circulars.png', type: 'image/png', sizes: '192x192' }],
        },
      ],
    },
  }

  return {
    plugins: [
      Vue(vueConfig),
      Vuetify(),
      Html(htmlConfig),
      VitePWA(pwaConfig),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '$': fileURLToPath(new URL('./public', import.meta.url)),
      },
    },
    build: {
      sourcemap: true,
    },
  }
})
