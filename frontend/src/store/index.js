import Vue from 'vue';
import Vuex from 'vuex';
import authModule from '@/store/modules/auth';
import dashboardModule from '@/store/modules/dashboard';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    authModule,
    dashboardModule,
  },
});
