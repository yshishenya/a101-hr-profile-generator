/**
 * Application entry point
 * Initializes Vue app with Pinia, Vuetify, and Router
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import vuetify from './plugins/vuetify'
import router from './router'
import App from './App.vue'
import './style.css'

// Create Vue app
const app = createApp(App)

// Create Pinia store
const pinia = createPinia()

// Register plugins
app.use(pinia)       // State management (must be before router)
app.use(vuetify)     // UI framework
app.use(router)      // Routing

// Mount app
app.mount('#app')
