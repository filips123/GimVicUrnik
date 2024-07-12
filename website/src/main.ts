import './assets/main.css'

import { createApp } from 'vue'

import App from './App.vue'
import pinia from './plugins/pinia'
import vuetify from './plugins/vuetify'
import router from './router'
import registerSentry from './sentry'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)

registerSentry(app, router)

app.mount('#app')
