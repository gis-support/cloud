import Vue from "vue";
import Swagger from "swagger-client"; // do podglądania api w monuted
import VueAlertify from "vue-alertify";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import i18n from "./i18n";
import api from "./docs/api.json"; // do podglądania api w monuted
import axios from "axios";
import VModal from "vue-js-modal";

import "bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "./assets/css/mvpready-admin.css";
import "ol/ol.css";

Vue.prototype.$swagger = new Swagger({ spec: api }).client; // do podglądania api w monuted
Vue.config.productionTip = false;
Vue.use(VueAlertify);
Vue.prototype.$http = axios;
Vue.use(VModal, { componentName: "modal" });

window.vm = new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount("#app");
