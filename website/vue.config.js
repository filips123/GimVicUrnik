process.env.VUE_APP_VERSION = require('./package.json').version

const path = require('path')

const SentryWebpackPlugin = require('@sentry/webpack-plugin')
const PreloadWebpackPlugin = require('@vue/preload-webpack-plugin')
const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  pwa: {
    name: process.env.VUE_APP_TITLE,
    manifestPath: 'site.webmanifest',

    themeColor: '#007300',
    msTileColor: '#007300',

    workboxOptions: {
      navigateFallback: '/index.html',
      navigateFallbackDenylist: [/\./, /\/api(?:[/?].*)?$/]
    },

    manifestOptions: {
      name: process.env.VUE_APP_TITLE,
      short_name: process.env.VUE_APP_SHORT,
      description: process.env.VUE_APP_DESCRIPTION,
      categories: process.env.VUE_APP_CATEGORIES.split(','),
      keywords: process.env.VUE_APP_KEYWORDS.split(','),

      theme_color: '#007300',
      background_color: '#ffffff',

      scope: '/',
      start_url: '/',

      shortcuts: [
        {
          name: 'Urnik',
          url: '/timetable',
          icons: [{
            src: '/img/shortcuts/timetable.png',
            type: 'image/png',
            sizes: '192x192'
          }]
        },
        {
          name: 'Jedilnik',
          url: '/menus',
          icons: [{
            src: '/img/shortcuts/menus.png',
            type: 'image/png',
            sizes: '192x192'
          }]
        },
        {
          name: 'Okrožnice',
          url: '/documents',
          icons: [{
            src: '/img/shortcuts/documents.png',
            type: 'image/png',
            sizes: '192x192'
          }]
        }
      ]
    }
  },

  chainWebpack: config => {
    config.plugin('preload').use(PreloadWebpackPlugin, [{
      rel: 'preload',
      include: {
        type: 'allChunks',
        chunks: ['app', 'chunk-vendors', 'home', 'timetable']
      },
      as (entry) {
        if (/\.css$/.test(entry)) return 'style'
        if (/\.woff$/.test(entry)) return 'font'
        if (/\.woff2$/.test(entry)) return 'font'
        if (/\.png$/.test(entry)) return 'image'
        if (/\.svg$/.test(entry)) return 'image'
        return 'script'
      }
    }])
  },

  configureWebpack: (config) => {
    config.output.devtoolFallbackModuleFilenameTemplate = 'webpack:///[resource-path]?[hash]'

    config.output.devtoolModuleFilenameTemplate = info => {
      const isVue = info.resourcePath.match(/\.vue$/)
      const isScript = info.query.match(/type=script/)
      const hasModuleId = info.moduleId !== ''

      const resourcePath = path.normalize(info.resourcePath).replaceAll('\\', '/')

      if (isVue && (!isScript || hasModuleId)) {
        // Detect generated files, filter as webpack-generated
        return `webpack-generated:///${resourcePath}?${info.hash}`
      } else {
        // If not generated, filter as webpack
        return `webpack:///${resourcePath}`
      }
    }

    // Upload sourcemaps to Sentry if enabled
    if (process.env.SENTRY_UPLOAD_SOURCEMAPS === 'true') {
      const releasePrefix = process.env.VUE_APP_SENTRY_RELEASE_PREFIX || ''
      const releaseSuffix = process.env.VUE_APP_SENTRY_RELEASE_SUFFIX || ''
      const releaseVersion = releasePrefix + process.env.VUE_APP_VERSION + releaseSuffix

      config.plugins.push(new SentryWebpackPlugin({
        org: process.env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT,
        authToken: process.env.SENTRY_AUTH_TOKEN,
        release: releaseVersion,
        include: './dist',
        finalize: false
      }))
    }
  }
})
