import Vue from 'vue';
import Vuex from 'vuex';
import authModule from '@/store/modules/auth';
import dashboardModule from '@/store/modules/dashboard';
import usersModule from '@/store/modules/users';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    authModule,
    dashboardModule,
    usersModule,
  },
});
