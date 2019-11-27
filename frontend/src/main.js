import Vue from 'vue';
import Swagger from 'swagger-client';
import App from './App.vue';
import router from './router';
import store from './store';
import i18n from './i18n';
import api from './docs/api.json';

import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './assets/css/mvpready-admin.css';


Vue.prototype.$swagger = new Swagger({ spec: api }).client;
Vue.config.productionTip = false;

window.vm = new Vue({
  router,
  store,
  i18n,
  render: h => h(App),
}).$mount('#app');
