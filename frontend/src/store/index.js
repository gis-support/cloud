import Vue from "vue";
import Vuex from "vuex";
import authModule from "@/store/modules/auth";
import dashboardModule from "@/store/modules/dashboard";
import featureManagerModule from "@/store/modules/featureManager";
import usersModule from "@/store/modules/users";
import tagsModule from "@/store/modules/tags";
import projectsModule from "@/store/modules/projects";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    authModule,
    dashboardModule,
    featureManagerModule,
    usersModule,
    tagsModule,
    projectsModule
  }
});
