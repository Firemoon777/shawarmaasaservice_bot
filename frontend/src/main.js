import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// import { BootstrapVue } from 'bootstrap-vue'

import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.js'
import axios from "axios";

const app = createApp(App)

axios.defaults.baseURL = "https://shaas.f1remoon.com/api"

app.use(router)

app.mount('#app')
