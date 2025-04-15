import './assets/main.css'

import { createApp } from 'vue'
import { VueFire } from 'vuefire'

import App from './App.vue'
import firebaseApp from './plugins/firebase'
import pinia from './plugins/pinia'
import vuetify from './plugins/vuetify'
import registerSentry from './registerSentry'
import registerServiceWorker from './registerServiceWorker'
import router from './router'

const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)
app.use(VueFire, { firebaseApp })

registerSentry(app, router)
registerServiceWorker(router)

app.mount('#app')
