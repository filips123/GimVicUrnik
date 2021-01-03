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

    themeColor: '#007300',
    msTileColor: '#007300',

    manifestOptions: {
      name: process.env.VUE_APP_TITLE,
      short_name: process.env.VUE_APP_SHORT,
      description: process.env.VUE_APP_DESCRIPTION,
      keywords: process.env.VUE_APP_KEYWORDS.split(','),

      theme_color: '#007300',
      background_color: '#ffffff',

      start_url: process.env.BASE_URL
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
