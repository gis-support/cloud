import Vue from "vue";
import VueRouter from "vue-router";
import store from "@/store";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    redirect: "/dashboard"
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import(/* webpackChunkName: "dashboard" */ "../views/Dashboard.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/feature_manager/:layerId",
    name: "feature_manager",
    component: () => import(/* webpackChunkName: "dashboard" */ "../views/FeatureManager.vue"),
    meta: {
      requiresAuth: true
    },
    props: true
  },
  {
    path: "/feature_manager",
    name: "project_manager",
    component: () => import(/* webpackChunkName: "dashboard" */ "../views/FeatureManager.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/login",
    name: "login",
    component: () => import(/* webpackChunkName: "login" */ "../views/Login.vue")
  },
  {
    path: "/users",
    name: "users",
    component: () => import(/* webpackChunkName: "users" */ "../views/Users.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/settings/:layerId",
    name: "settings",
    component: () => import(/* webpackChunkName: "settings" */ "../views/Settings.vue"),
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/settings",
    name: "appSettings",
    component: () => import(/* webpackChunkName: "settings" */ "../views/AppSettings.vue"),
    meta: {
      requiresAuth: true
    }
  }
];

const router = new VueRouter({
  mode: "history",
  routes
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    setTimeout(() => {
      store.dispatch("checkToken").then(r => {
        if (r.body.token === "valid") {
          next();
        } else {
          store.commit("logOut");
          next({
            name: "login"
          });
        }
      });
    }, 0);
  } else {
    next();
  }
});

export default router;
