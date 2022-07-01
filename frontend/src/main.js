import Vue from 'vue'
import App from './App.vue'
import { loadScript } from "vue-plugin-load-script";

Vue.config.productionTip = false

loadScript("https://telegram.org/js/telegram-web-app.js")

new Vue({
  render: h => h(App),
}).$mount('#app')
