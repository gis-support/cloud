import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '@/store';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import(/* webpackChunkName: "dashboard" */ '../views/Dashboard.vue'),
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/feature_manager/:layerId',
    name: 'feature_manager',
    component: () => import(/* webpackChunkName: "dashboard" */ '../views/FeatureManager.vue'),
    meta: {
      requiresAuth: true,
    },
    props: true,
  },
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "login" */ '../views/Login.vue'),
  },
  {
    path: '/users',
    name: 'users',
    component: () => import(/* webpackChunkName: "users" */ '../views/Users.vue'),
  },
];

const router = new VueRouter({
  mode: 'history',
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!store.getters.getLogged) {
      // TODO - Dodać sprawdzanie tokena po backendzie
      next({
        name: 'login',
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
