// eslint-disable-next-line @typescript-eslint/no-var-requires
process.env.VUE_APP_VERSION = require('./package.json').version

module.exports = {
  transpileDependencies: [
    'vuex-module-decorators',
    'vuex-persist',
    'vuetify'
  ],

  pwa: {
    name: process.env.VUE_APP_TITLE,
    manifestPath: 'site.webmanifest',

    themeColor: '#007300',
    msTileColor: '#007300',

    workboxOptions: {
      navigateFallback: '/index.html',
      navigateFallbackBlacklist: [/\./]
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
    config.plugin('preload').tap(options => {
      options[0].include = {
        type: 'allChunks',
        chunks: ['app', 'chunk-vendors', 'home', 'timetable']
      }
      return options
    })
  }
}
