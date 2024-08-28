import './assets/main.css'

import { createApp } from 'vue'

import App from './App.vue'
import pinia from './plugins/pinia'
import vuetify from './plugins/vuetify'
import registerSentry from './registerSentry'
import registerServiceWorker from './registerServiceWorker'
import router from './router'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)

registerSentry(app, router)
registerServiceWorker(router)

app.mount('#app')
