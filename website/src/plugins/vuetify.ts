import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import sl from 'vuetify/src/locale/sl'

import { SettingsModule, ThemeType } from '@/store/modules/settings'

Vue.use(Vuetify)

export default new Vuetify({
  lang: {
    locales: { sl },
    current: 'sl'
  },
  icons: {
    iconfont: 'mdiSvg'
  },
  theme: {
    dark: (SettingsModule.theme === ThemeType.System && window.matchMedia('(prefers-color-scheme: dark)').matches) || SettingsModule.theme === ThemeType.Dark
  }
})
