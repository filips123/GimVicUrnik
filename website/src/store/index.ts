import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'

Vue.use(Vuex)

const vuexLocalSettings = new VuexPersistence({
  modules: ['settings'],
  key: 'settings'
})

const vuexLocalStorage = new VuexPersistence({
  modules: ['storage'],
  key: 'storage'
})

export default new Vuex.Store({
  strict: process.env.NODE_ENV !== 'production',
  plugins: [
    vuexLocalSettings.plugin,
    vuexLocalStorage.plugin
  ]
})
